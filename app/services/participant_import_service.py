"""
Participant Import Service - Handles importing participants from Google Sheets
"""

import logging
from datetime import datetime
from app import db
from app.models import Participant, Event
from .google_service import GoogleService

logger = logging.getLogger(__name__)


class ParticipantImportService:
    """Service to import participants from Google Sheets"""

    def __init__(self):
        self.google_service = GoogleService()

    def import_from_sheet(self, spreadsheet_id, event_id, sheet_range='A2:Z1000',
                         column_mapping=None, skip_duplicates=True):
        """
        Import participants from a Google Sheet

        Args:
            spreadsheet_id: Google Sheets ID
            event_id: Event ID to associate participants with
            sheet_range: Range to read (default: A2:Z1000, skipping header row)
            column_mapping: Dict mapping column indices to field names
                           Default: {0: 'nome', 1: 'email', 2: 'telefone', 3: 'empresa'}
            skip_duplicates: If True, skip participants already in the event

        Returns:
            dict with import statistics
        """
        # Verify event exists
        event = Event.query.get(event_id)
        if not event or event.deleted_at:
            raise ValueError(f"Evento {event_id} não encontrado")

        # Default column mapping
        if column_mapping is None:
            column_mapping = {
                0: 'nome',
                1: 'email',
                2: 'telefone',
                3: 'empresa',
                4: 'observacoes'
            }

        # Authenticate and get data
        self.google_service.authenticate()
        rows = self.google_service.get_spreadsheet_data(spreadsheet_id, sheet_range)

        stats = {
            'total_rows': len(rows),
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'error_details': []
        }

        for idx, row in enumerate(rows, start=2):  # Start at 2 (1 is header)
            try:
                # Extract data based on column mapping
                participant_data = {}
                for col_idx, field_name in column_mapping.items():
                    if col_idx < len(row):
                        value = row[col_idx].strip() if row[col_idx] else None
                        if value:  # Only add non-empty values
                            participant_data[field_name] = value

                # Validate required fields
                if 'nome' not in participant_data or 'email' not in participant_data:
                    stats['skipped'] += 1
                    stats['error_details'].append({
                        'row': idx,
                        'error': 'Nome ou email em falta',
                        'data': row
                    })
                    continue

                # Check for duplicates
                if skip_duplicates:
                    existing = Participant.query.filter_by(
                        email=participant_data['email'],
                        evento_id=event_id,
                        deleted_at=None
                    ).first()

                    if existing:
                        stats['skipped'] += 1
                        logger.info(f"Participante duplicado ignorado: {participant_data['email']}")
                        continue

                # Create participant
                participant = Participant(
                    nome=participant_data['nome'],
                    email=participant_data['email'],
                    evento_id=event_id,
                    telefone=participant_data.get('telefone'),
                    empresa=participant_data.get('empresa'),
                    observacoes=participant_data.get('observacoes'),
                    status='pendente'
                )

                db.session.add(participant)
                db.session.commit()
                stats['imported'] += 1

                logger.info(f"Participante importado: {participant.nome} ({participant.email})")

            except Exception as e:
                stats['errors'] += 1
                stats['error_details'].append({
                    'row': idx,
                    'error': str(e),
                    'data': row
                })
                logger.error(f"Erro ao importar linha {idx}: {e}")
                db.session.rollback()

        return stats

    def import_from_form_responses(self, form_id, event_id, skip_duplicates=True):
        """
        Import participants from Google Form responses

        Args:
            form_id: Google Form ID
            event_id: Event ID to associate participants with
            skip_duplicates: If True, skip participants already in the event

        Returns:
            dict with import statistics
        """
        # Verify event exists
        event = Event.query.get(event_id)
        if not event or event.deleted_at:
            raise ValueError(f"Evento {event_id} não encontrado")

        # Authenticate and get responses
        self.google_service.authenticate()
        responses = self.google_service.get_form_responses(form_id)

        stats = {
            'total_responses': len(responses),
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'error_details': []
        }

        for idx, response in enumerate(responses, start=1):
            try:
                # Extract answers from response
                answers = response.get('answers', {})
                participant_data = {}

                # Parse answers (Google Forms returns complex structure)
                for question_id, answer_data in answers.items():
                    # Get the question text from textAnswers
                    text_answers = answer_data.get('textAnswers', {})
                    if text_answers:
                        answer_value = text_answers.get('answers', [{}])[0].get('value', '')

                        # Try to map based on question text
                        # This is a simple mapping - you might need to adjust based on your forms
                        question_text = answer_data.get('questionId', '').lower()

                        if 'nome' in question_text or 'name' in question_text:
                            participant_data['nome'] = answer_value
                        elif 'email' in question_text or 'e-mail' in question_text:
                            participant_data['email'] = answer_value
                        elif 'telefone' in question_text or 'phone' in question_text:
                            participant_data['telefone'] = answer_value
                        elif 'empresa' in question_text or 'company' in question_text:
                            participant_data['empresa'] = answer_value

                # Validate required fields
                if 'nome' not in participant_data or 'email' not in participant_data:
                    stats['skipped'] += 1
                    stats['error_details'].append({
                        'response_id': response.get('responseId'),
                        'error': 'Nome ou email em falta'
                    })
                    continue

                # Check for duplicates
                if skip_duplicates:
                    existing = Participant.query.filter_by(
                        email=participant_data['email'],
                        evento_id=event_id,
                        deleted_at=None
                    ).first()

                    if existing:
                        stats['skipped'] += 1
                        continue

                # Create participant
                participant = Participant(
                    nome=participant_data['nome'],
                    email=participant_data['email'],
                    evento_id=event_id,
                    telefone=participant_data.get('telefone'),
                    empresa=participant_data.get('empresa'),
                    status='confirmado'  # Form responses are confirmed
                )

                db.session.add(participant)
                db.session.commit()
                stats['imported'] += 1

                logger.info(f"Participante importado do form: {participant.nome}")

            except Exception as e:
                stats['errors'] += 1
                stats['error_details'].append({
                    'response_id': response.get('responseId'),
                    'error': str(e)
                })
                logger.error(f"Erro ao importar resposta {idx}: {e}")
                db.session.rollback()

        return stats

    def preview_sheet_data(self, spreadsheet_id, sheet_range='A1:Z100'):
        """
        Preview data from Google Sheet before importing

        Returns first 10 rows for validation
        """
        self.google_service.authenticate()
        rows = self.google_service.get_spreadsheet_data(spreadsheet_id, sheet_range)

        return {
            'total_rows': len(rows),
            'preview': rows[:10],  # First 10 rows
            'columns': rows[0] if rows else []  # Header row
        }

    def get_available_sheets(self, limit=50):
        """Get list of available Google Sheets"""
        self.google_service.authenticate()
        return self.google_service.list_spreadsheets(limit)
