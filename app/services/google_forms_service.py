"""
Google Forms Service - Create and manage Google Forms for events
"""

from app.services.google_auth_service import GoogleAuthService


class GoogleFormsService:
    """Service to create and manage Google Forms"""

    def __init__(self):
        self.auth_service = GoogleAuthService()

    def create_event_form(self, evento):
        """
        Create a Google Form for event registration

        Args:
            evento: Event model instance

        Returns:
            dict with form_id, form_url, sheet_id, sheet_url
        """
        forms_service = self.auth_service.get_forms_service()
        sheets_service = self.auth_service.get_sheets_service()
        drive_service = self.auth_service.get_drive_service()

        if not forms_service or not sheets_service:
            raise Exception("Google authentication required")

        # Create the form with event date in title
        data_str = evento.data_inicio.strftime('%d/%m/%Y')
        if evento.data_fim and evento.data_fim != evento.data_inicio:
            data_str = f"{evento.data_inicio.strftime('%d/%m/%Y')} a {evento.data_fim.strftime('%d/%m/%Y')}"

        form_title = f"Inscrição: {evento.nome} ({data_str})"
        form_doc_title = f"Inscrição_{evento.nome.replace(' ', '_')}_{evento.data_inicio.strftime('%Y%m%d')}"

        form = {
            "info": {
                "title": form_title,
                "documentTitle": form_doc_title,
            }
        }

        result = forms_service.forms().create(body=form).execute()
        form_id = result['formId']

        # Add form description
        update = {
            "requests": [
                {
                    "updateFormInfo": {
                        "info": {
                            "description": self._build_form_description(evento)
                        },
                        "updateMask": "description"
                    }
                }
            ]
        }
        forms_service.forms().batchUpdate(formId=form_id, body=update).execute()

        # Add form questions
        questions = self._build_form_questions(evento)
        forms_service.forms().batchUpdate(formId=form_id, body=questions).execute()

        # Create response spreadsheet
        sheet_data = {
            "requests": [
                {
                    "createSheet": {
                        "properties": {
                            "title": "Respostas",
                            "gridProperties": {
                                "rowCount": 1000,
                                "columnCount": 20
                            }
                        }
                    }
                }
            ]
        }

        # Link form to spreadsheet (via Drive API)
        form_url = f"https://docs.google.com/forms/d/{form_id}/edit"
        response_url = f"https://docs.google.com/forms/d/{form_id}/responses"

        # Get form responses spreadsheet ID (if created)
        # Note: Google Forms automatically creates a spreadsheet when you link it
        # For now, we'll return None for sheet_id and implement proper linking later

        return {
            'form_id': form_id,
            'form_url': form_url,
            'response_url': response_url,
            'sheet_id': None,  # Will be set after manual linking or via advanced setup
            'sheet_url': None
        }

    def _build_form_description(self, evento):
        """Build form description from event data"""
        description = f"""
Formulário de inscrição para o evento:

📅 **Data**: {evento.data_inicio.strftime('%d/%m/%Y')}
"""
        if evento.data_fim:
            description += f" a {evento.data_fim.strftime('%d/%m/%Y')}"

        description += f"\n⏱️ **Duração**: {evento.duracao_horas} horas\n"

        if evento.formadora:
            description += f"👩‍🏫 **Formadora**: {evento.formadora}\n"

        if evento.local:
            description += f"📍 **Local**: {evento.local}\n"

        if evento.descricao:
            description += f"\n{evento.descricao}\n"

        description += "\nPor favor, preencha os campos abaixo para se inscrever."

        return description

    def _build_form_questions(self, evento):
        """Build form questions"""
        return {
            "requests": [
                # Question 1: Nome
                {
                    "createItem": {
                        "item": {
                            "title": "Nome Completo",
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "textQuestion": {
                                        "paragraph": False
                                    }
                                }
                            }
                        },
                        "location": {"index": 0}
                    }
                },
                # Question 2: Email
                {
                    "createItem": {
                        "item": {
                            "title": "Email",
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "textQuestion": {
                                        "paragraph": False
                                    }
                                }
                            }
                        },
                        "location": {"index": 1}
                    }
                },
                # Question 3: Telefone
                {
                    "createItem": {
                        "item": {
                            "title": "Telefone",
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "textQuestion": {
                                        "paragraph": False
                                    }
                                }
                            }
                        },
                        "location": {"index": 2}
                    }
                },
                # Question 4: Empresa (optional)
                {
                    "createItem": {
                        "item": {
                            "title": "Empresa (opcional)",
                            "questionItem": {
                                "question": {
                                    "required": False,
                                    "textQuestion": {
                                        "paragraph": False
                                    }
                                }
                            }
                        },
                        "location": {"index": 3}
                    }
                },
                # Question 5: Observações (optional)
                {
                    "createItem": {
                        "item": {
                            "title": "Observações (opcional)",
                            "description": "Informações adicionais, restrições alimentares, necessidades especiais, etc.",
                            "questionItem": {
                                "question": {
                                    "required": False,
                                    "textQuestion": {
                                        "paragraph": True
                                    }
                                }
                            }
                        },
                        "location": {"index": 4}
                    }
                }
            ]
        }

    def get_form_responses(self, form_id):
        """
        Get all responses from a Google Form

        Args:
            form_id: Google Form ID

        Returns:
            List of response dictionaries
        """
        forms_service = self.auth_service.get_forms_service()

        if not forms_service:
            raise Exception("Google authentication required")

        form = forms_service.forms().get(formId=form_id).execute()
        responses = forms_service.forms().responses().list(formId=form_id).execute()

        if 'responses' not in responses:
            return []

        # Parse responses
        parsed_responses = []
        for response in responses.get('responses', []):
            parsed = self._parse_form_response(response, form)
            parsed_responses.append(parsed)

        return parsed_responses

    def _parse_form_response(self, response, form):
        """Parse a single form response"""
        answers = response.get('answers', {})

        # Map question IDs to titles
        question_map = {}
        for item in form.get('items', []):
            if 'questionItem' in item:
                question_id = item['questionItem']['question']['questionId']
                question_map[question_id] = item['title']

        # Extract participant data
        participant_data = {
            'response_id': response.get('responseId'),
            'timestamp': response.get('createTime'),
            'nome': '',
            'email': '',
            'telefone': '',
            'empresa': '',
            'observacoes': ''
        }

        for question_id, answer in answers.items():
            question_title = question_map.get(question_id, '')
            text_answer = answer.get('textAnswers', {}).get('answers', [{}])[0].get('value', '')

            # Map to participant fields
            if 'nome' in question_title.lower():
                participant_data['nome'] = text_answer
            elif 'email' in question_title.lower() or 'e-mail' in question_title.lower():
                participant_data['email'] = text_answer
            elif 'telefone' in question_title.lower() or 'telemóvel' in question_title.lower():
                participant_data['telefone'] = text_answer
            elif 'empresa' in question_title.lower():
                participant_data['empresa'] = text_answer
            elif 'observa' in question_title.lower():
                participant_data['observacoes'] = text_answer

        return participant_data

    def list_recent_forms(self, limit=100):
        """
        List recent Google Forms from Drive

        Args:
            limit: Maximum number of forms to return (default 100)

        Returns:
            List of dictionaries with form info (id, name, created_time, modified_time, url)
        """
        drive_service = self.auth_service.get_drive_service()

        if not drive_service:
            raise Exception("Google authentication required")

        try:
            # Query for Google Forms files
            # mimeType for Google Forms is 'application/vnd.google-apps.form'
            query = "mimeType='application/vnd.google-apps.form' and trashed=false"

            all_forms = []
            page_token = None

            # Paginate through all results up to limit
            while len(all_forms) < limit:
                # Try 'user' first (user's drive), then 'allDrives' if needed
                try:
                    results = drive_service.files().list(
                        q=query,
                        pageSize=min(100, limit - len(all_forms)),
                        orderBy='modifiedTime desc',
                        fields='nextPageToken, files(id, name, createdTime, modifiedTime, webViewLink, owners)',
                        supportsAllDrives=False,
                        includeItemsFromAllDrives=False,
                        pageToken=page_token,
                        corpora='user'  # Search only in user's drive
                    ).execute()
                except Exception as e:
                    print(f"Error with 'user' corpora, trying 'allDrives': {e}")
                    # Fallback to allDrives if user doesn't work
                    results = drive_service.files().list(
                        q=query,
                        pageSize=min(100, limit - len(all_forms)),
                        orderBy='modifiedTime desc',
                        fields='nextPageToken, files(id, name, createdTime, modifiedTime, webViewLink, owners)',
                        supportsAllDrives=True,
                        includeItemsFromAllDrives=True,
                        pageToken=page_token,
                        corpora='allDrives'
                    ).execute()

                forms = results.get('files', [])
                if not forms:
                    break

                all_forms.extend(forms)

                # Check if there are more pages
                page_token = results.get('nextPageToken')
                if not page_token:
                    break

            # Format the results
            formatted_forms = []
            for form in all_forms:
                # Get owner name if available
                owner_name = 'Unknown'
                owners = form.get('owners', [])
                if owners:
                    owner_name = owners[0].get('displayName', owners[0].get('emailAddress', 'Unknown'))

                form_name = form.get('name', '')

                # Try to extract date from form name (format: dd/mm/yyyy or yyyy-mm-dd or yyyymmdd)
                event_date = self._extract_date_from_name(form_name)

                formatted_forms.append({
                    'id': form.get('id'),
                    'name': form_name,
                    'created_time': form.get('createdTime'),
                    'modified_time': form.get('modifiedTime'),
                    'url': form.get('webViewLink', f"https://docs.google.com/forms/d/{form.get('id')}/edit"),
                    'owner': owner_name,
                    'event_date': event_date  # Extracted date if found
                })

            print(f"DEBUG - Found {len(formatted_forms)} forms total")
            return formatted_forms

        except Exception as e:
            print(f"Error listing forms: {e}")
            import traceback
            traceback.print_exc()
            return []

    def search_forms_by_name(self, search_term, limit=20):
        """
        Search Google Forms by name

        Args:
            search_term: Text to search in form names
            limit: Maximum number of results (default 20)

        Returns:
            List of dictionaries with form info
        """
        drive_service = self.auth_service.get_drive_service()

        if not drive_service:
            raise Exception("Google authentication required")

        try:
            # Query for Google Forms with name containing search term
            query = f"mimeType='application/vnd.google-apps.form' and trashed=false and name contains '{search_term}'"

            results = drive_service.files().list(
                q=query,
                pageSize=limit,
                orderBy='modifiedTime desc',
                fields='files(id, name, createdTime, modifiedTime, webViewLink)',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True
            ).execute()

            forms = results.get('files', [])

            # Format the results
            formatted_forms = []
            for form in forms:
                formatted_forms.append({
                    'id': form.get('id'),
                    'name': form.get('name'),
                    'created_time': form.get('createdTime'),
                    'modified_time': form.get('modifiedTime'),
                    'url': form.get('webViewLink', f"https://docs.google.com/forms/d/{form.get('id')}/edit")
                })

            return formatted_forms

        except Exception as e:
            print(f"Error searching forms: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_form_info(self, form_id):
        """
        Get detailed information about a specific form

        Args:
            form_id: Google Form ID

        Returns:
            Dictionary with form information
        """
        forms_service = self.auth_service.get_forms_service()
        drive_service = self.auth_service.get_drive_service()

        if not forms_service or not drive_service:
            raise Exception("Google authentication required")

        try:
            # Get form metadata from Forms API
            form = forms_service.forms().get(formId=form_id).execute()

            # Get file metadata from Drive API
            file_metadata = drive_service.files().get(
                fileId=form_id,
                fields='id, name, createdTime, modifiedTime, webViewLink'
            ).execute()

            return {
                'id': form_id,
                'title': form.get('info', {}).get('title', ''),
                'description': form.get('info', {}).get('description', ''),
                'name': file_metadata.get('name', ''),
                'created_time': file_metadata.get('createdTime'),
                'modified_time': file_metadata.get('modifiedTime'),
                'url': file_metadata.get('webViewLink', f"https://docs.google.com/forms/d/{form_id}/edit"),
                'question_count': len(form.get('items', []))
            }

        except Exception as e:
            print(f"Error getting form info: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_date_from_name(self, name):
        """
        Extract date from form name
        Supports formats: dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd, yyyymmdd, (dd/mm/yyyy)

        Returns:
            Date string in format dd/mm/yyyy or None
        """
        import re
        from datetime import datetime

        if not name:
            return None

        # Pattern 1: (dd/mm/yyyy) or (dd/mm/yy)
        match = re.search(r'\((\d{1,2})/(\d{1,2})/(\d{2,4})\)', name)
        if match:
            day, month, year = match.groups()
            if len(year) == 2:
                year = f"20{year}"
            try:
                date = datetime(int(year), int(month), int(day))
                return date.strftime('%d/%m/%Y')
            except:
                pass

        # Pattern 2: dd/mm/yyyy or dd-mm-yyyy
        match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', name)
        if match:
            day, month, year = match.groups()
            if len(year) == 2:
                year = f"20{year}"
            try:
                date = datetime(int(year), int(month), int(day))
                return date.strftime('%d/%m/%Y')
            except:
                pass

        # Pattern 3: yyyymmdd (8 digits)
        match = re.search(r'_(\d{8})(?:[_\s]|$)', name)
        if match:
            date_str = match.group(1)
            try:
                date = datetime.strptime(date_str, '%Y%m%d')
                return date.strftime('%d/%m/%Y')
            except:
                pass

        # Pattern 4: yyyy-mm-dd
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})', name)
        if match:
            year, month, day = match.groups()
            try:
                date = datetime(int(year), int(month), int(day))
                return date.strftime('%d/%m/%Y')
            except:
                pass

        return None

    def delete_form(self, form_id):
        """Delete a Google Form"""
        drive_service = self.auth_service.get_drive_service()

        if not drive_service:
            raise Exception("Google authentication required")

        try:
            drive_service.files().delete(fileId=form_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting form: {e}")
            return False
