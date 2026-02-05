"""
Main blueprint - Frontend routes
Adapted from v1 to work with v2 architecture
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from app.models import Event, Participant, User, Organization
from app import db

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Homepage - Beautiful landing page"""
    # Get organizations for display
    organizacoes = Organization.query.filter_by(ativa=True).order_by(Organization.id).all()
    return render_template('menu_principal.html', organizacoes=organizacoes)


@bp.route('/logos/<path:filename>')
def serve_logo(filename):
    """Serve logo files"""
    import os
    from flask import send_from_directory
    logos_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'Logos')
    return send_from_directory(logos_dir, filename)


@bp.route('/eventos')
def eventos():
    """Default events page - redirects to menu"""
    # Redirect to main menu to avoid confusion
    flash('Por favor, escolha uma organização', 'info')
    return redirect(url_for('main.index'))


@bp.route('/eventos_anarita')
def eventos_anarita():
    """List Ana Rita - Mindset & Wellness events"""
    org = Organization.query.filter_by(slug='ana-rita-mindset-wellness', ativa=True).first_or_404()
    eventos = Event.query.filter(Event.deleted_at.is_(None), Event.organizacao_id == org.id).all()
    return render_template('eventos.html', eventos=eventos, organizacao=org)


@bp.route('/eventos_ardaterra')
def eventos_ardaterra():
    """List ARdaTerra events"""
    org = Organization.query.filter_by(slug='ardaterra', ativa=True).first_or_404()
    eventos = Event.query.filter(Event.deleted_at.is_(None), Event.organizacao_id == org.id).all()
    return render_template('eventos.html', eventos=eventos, organizacao=org)


@bp.route('/detalhe_evento/<int:id>')
def detalhe_evento(id):
    """Event details with participants"""
    evento = Event.query.get_or_404(id)
    participantes = Participant.query.filter_by(evento_id=id).filter(
        Participant.deleted_at.is_(None)
    ).all()

    return render_template('detalhe_evento.html', evento=evento, participantes=participantes)


@bp.route('/utilizadores')
def utilizadores():
    """List all users"""
    users = User.query.filter(User.deleted_at.is_(None)).all()
    return render_template('utilizadores.html', utilizadores=users)


@bp.route('/gestao_automatica')
def gestao_automatica():
    """Automation management page"""
    from app.services.google_auth_service import GoogleAuthService  # v2.1 - OAuth HTTP fix

    # Check Google authentication status
    auth_service = GoogleAuthService()
    google_connected = auth_service.is_authenticated()

    eventos = Event.query.filter(Event.deleted_at.is_(None)).all()

    # Convert eventos to dict for JSON serialization
    eventos_json = [{
        'id': e.id,
        'nome': e.nome,
        'data_inicio': e.data_inicio.isoformat() if e.data_inicio else None,
        'google_form_id': e.google_form_id
    } for e in eventos]

    return render_template('gestao_automatica.html',
                         google_connected=google_connected,
                         eventos=eventos,
                         eventos_json=eventos_json)


@bp.route('/criar_evento', methods=['GET', 'POST'])
def criar_evento():
    """Create new event - supports manual form or Excel upload"""
    if request.method == 'POST':
        try:
            # Check if Excel file was uploaded
            if 'excel_file' in request.files and request.files['excel_file'].filename:
                return criar_evento_from_excel()

            # Manual form submission
            from datetime import datetime

            # Parse data
            data_str = request.form.get('data') or request.form.get('data_inicio')
            data_inicio = datetime.strptime(data_str, '%d/%m/%y').date() if data_str else None

            data_fim_str = request.form.get('data_fim')
            data_fim = datetime.strptime(data_fim_str, '%d/%m/%y').date() if data_fim_str else None

            # Get organization ID from form or session
            organizacao_id = request.form.get('organizacao_id', type=int)
            if not organizacao_id:
                # Default to Ana Rita (ID: 1) if not specified
                organizacao_id = 1

            evento = Event(
                nome=request.form['nome'],
                data_inicio=data_inicio,
                data_fim=data_fim,
                duracao_minutos=int(request.form.get('duracao', 60)),
                descricao=request.form.get('descricao', ''),
                formadora=request.form.get('formadora', ''),
                organizacao_id=organizacao_id
            )
            db.session.add(evento)
            db.session.commit()
            flash('Evento criado com sucesso!', 'success')
            # Redirect to appropriate organization page
            if organizacao_id == 2:  # ARdaTerra
                return redirect(url_for('main.eventos_ardaterra'))
            else:  # Ana Rita (default)
                return redirect(url_for('main.eventos_anarita'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar evento: {str(e)}', 'error')

    # Pass organizations to template for selection
    organizacoes = Organization.query.filter_by(ativa=True).all()
    # Get pre-selected organization from query param
    selected_org = request.args.get('org', type=int)
    return render_template('criar_evento.html', organizacoes=organizacoes, selected_org=selected_org)


def criar_evento_from_excel():
    """Create event and participants from Excel file"""
    from app.services.excel_import_service import ExcelImportService
    import os
    from flask import current_app

    try:
        excel_service = ExcelImportService()
        excel_file = request.files['excel_file']

        # Validate file
        is_valid, message = excel_service.validate_file(excel_file)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('main.criar_evento'))

        # Save file temporarily
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        filepath = excel_service.save_uploaded_file(excel_file, upload_folder)

        # Parse Excel
        data = excel_service.parse_excel_file(filepath)

        # Check if multi-event format or single event
        if 'events' in data:
            # Multi-event format
            events_list = data['events']
            print(f"DEBUG - Multi-event format detected: {len(events_list)} events")

            # Get organization ID from form
            organizacao_id = request.form.get('organizacao_id', type=int)
            if not organizacao_id:
                organizacao_id = 1  # Default to Ana Rita

            created_events = []
            total_participants = 0

            for event_item in events_list:
                event_data = event_item['event']
                participants_data = event_item['participants']

                # Validate required fields
                nome = event_data.get('nome', '').strip()
                if not nome:
                    flash('⚠️ Nome do evento é obrigatório. Evento ignorado.', 'warning')
                    continue

                # Convert dates
                data_inicio = event_data.get('data') or event_data.get('data_inicio')
                if data_inicio and hasattr(data_inicio, 'date'):
                    data_inicio = data_inicio.date()

                if not data_inicio:
                    flash(f'⚠️ Data de início é obrigatória para o evento "{nome}". Evento ignorado.', 'warning')
                    continue

                data_fim = event_data.get('data_fim')
                if data_fim and hasattr(data_fim, 'date'):
                    data_fim = data_fim.date()

                # Get duration in minutes
                duracao_minutos = event_data.get('duracao', 60)

                # Create event
                evento = Event(
                    nome=nome,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    duracao_minutos=duracao_minutos,
                    descricao=event_data.get('descricao', ''),
                    formadora=event_data.get('formadora', ''),
                    local=event_data.get('local', ''),
                    organizacao_id=organizacao_id
                )
                db.session.add(evento)
                db.session.flush()  # Get evento.id

                # Create participants for this event
                for participant_data in participants_data:
                    participante = Participant(
                        evento_id=evento.id,
                        nome=participant_data.get('nome', ''),
                        email=participant_data.get('email', ''),
                        telefone=participant_data.get('telefone', ''),
                        empresa=participant_data.get('empresa', ''),
                        observacoes=participant_data.get('observacoes', '')
                    )
                    db.session.add(participante)
                    total_participants += 1

                created_events.append(evento)

            db.session.commit()

            # Clean up
            try:
                os.remove(filepath)
            except:
                pass

            flash(f'{len(created_events)} eventos criados com sucesso! {total_participants} participantes importados.', 'success')
            # Redirect to appropriate organization page
            if organizacao_id == 2:  # ARdaTerra
                return redirect(url_for('main.eventos_ardaterra'))
            else:  # Ana Rita (default)
                return redirect(url_for('main.eventos_anarita'))

        else:
            # Single event format (legacy)
            event_data = data['event']
            participants_data = data['participants']

            print("DEBUG - Single event format")
            print(f"Event data: {event_data}")
            print(f"Participants count: {len(participants_data)}")

            # Validate required fields
            nome = event_data.get('nome', '').strip()
            if not nome:
                flash('⚠️ Nome do evento é obrigatório', 'error')
                return redirect(url_for('main.criar_evento'))

            # Convert dates
            data_inicio = event_data.get('data') or event_data.get('data_inicio')
            if data_inicio and hasattr(data_inicio, 'date'):
                data_inicio = data_inicio.date()

            if not data_inicio:
                flash('⚠️ Data de início é obrigatória', 'error')
                return redirect(url_for('main.criar_evento'))

            data_fim = event_data.get('data_fim')
            if data_fim and hasattr(data_fim, 'date'):
                data_fim = data_fim.date()

            # Get duration in minutes
            duracao_minutos = event_data.get('duracao', 60)

            evento = Event(
                nome=nome,
                data_inicio=data_inicio,
                data_fim=data_fim,
                duracao_minutos=duracao_minutos,
                descricao=event_data.get('descricao', ''),
                formadora=event_data.get('formadora', ''),
                local=event_data.get('local', '')
            )
            db.session.add(evento)
            db.session.flush()  # Get evento.id

            # Create participants
            participants_count = 0
            for participant_data in participants_data:
                participante = Participant(
                    evento_id=evento.id,
                    nome=participant_data.get('nome', ''),
                    email=participant_data.get('email', ''),
                    telefone=participant_data.get('telefone', ''),
                    empresa=participant_data.get('empresa', ''),
                    observacoes=participant_data.get('observacoes', '')
                )
                db.session.add(participante)
                participants_count += 1

            db.session.commit()

            # Clean up uploaded file
            try:
                os.remove(filepath)
            except:
                pass

            flash(f'Evento criado com sucesso! {participants_count} participantes importados.', 'success')
            return redirect(url_for('main.detalhe_evento', id=evento.id))

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()  # Print full error to console
        flash(f'Erro ao importar Excel: {str(e)}', 'error')
        return redirect(url_for('main.criar_evento'))


@bp.route('/editar_evento/<int:id>', methods=['GET', 'POST'])
def editar_evento(id):
    """Edit event"""
    evento = Event.query.get_or_404(id)

    if request.method == 'POST':
        try:
            from datetime import datetime

            evento.nome = request.form['nome']

            # Parse data
            data_str = request.form.get('data') or request.form.get('data_inicio')
            if data_str:
                evento.data_inicio = datetime.strptime(data_str, '%d/%m/%y').date()

            data_fim_str = request.form.get('data_fim')
            if data_fim_str:
                evento.data_fim = datetime.strptime(data_fim_str, '%d/%m/%y').date()
            else:
                evento.data_fim = None

            evento.duracao_minutos = int(request.form.get('duracao', 1))
            evento.descricao = request.form.get('descricao', '')
            evento.formadora = request.form.get('formadora', '')
            db.session.commit()
            flash('Evento atualizado com sucesso!', 'success')
            # Redirect to appropriate organization page
            if evento.organizacao_id == 2:  # ARdaTerra
                return redirect(url_for('main.eventos_ardaterra'))
            else:  # Ana Rita (default)
                return redirect(url_for('main.eventos_anarita'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar evento: {str(e)}', 'error')

    return render_template('editar_evento.html', evento=evento)


@bp.route('/apagar_evento/<int:id>', methods=['POST'])
def apagar_evento(id):
    """Soft delete event"""
    try:
        evento = Event.query.get_or_404(id)
        from datetime import datetime
        organizacao_id = evento.organizacao_id
        evento.deleted_at = datetime.utcnow()
        db.session.commit()
        flash('Evento apagado com sucesso!', 'success')

        # Redirect to appropriate organization page
        if organizacao_id == 2:  # ARdaTerra
            return redirect(url_for('main.eventos_ardaterra'))
        else:  # Ana Rita (default)
            return redirect(url_for('main.eventos_anarita'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao apagar evento: {str(e)}', 'error')
        return redirect(url_for('main.index'))


# Rotas de Gestão Automática
@bp.route('/google/authenticate')
def google_authenticate():
    """Start Google OAuth authentication flow"""
    from app.services.google_auth_service import GoogleAuthService
    from flask import request

    try:
        auth_service = GoogleAuthService()

        # Build redirect URI - use request.host_url to get correct base URL with port
        redirect_uri = request.host_url.rstrip('/') + '/google/callback'

        # Get authorization URL
        authorization_url = auth_service.get_authorization_url(redirect_uri)

        return redirect(authorization_url)
    except FileNotFoundError as e:
        flash(f'Erro: {str(e)}', 'error')
        flash('Por favor, configure as credenciais do Google Cloud Console', 'warning')
        return redirect(url_for('main.gestao_automatica'))
    except Exception as e:
        flash(f'Erro ao iniciar autenticação: {str(e)}', 'error')
        return redirect(url_for('main.gestao_automatica'))


@bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    from app.services.google_auth_service import GoogleAuthService
    from flask import request
    import traceback

    try:
        auth_service = GoogleAuthService()

        # Get full callback URL
        authorization_response = request.url
        # Use same redirect URI format as in google_authenticate
        redirect_uri = request.host_url.rstrip('/') + '/google/callback'

        print(f"DEBUG - Authorization response: {authorization_response[:100]}...")
        print(f"DEBUG - Redirect URI: {redirect_uri}")

        # Exchange code for credentials
        creds = auth_service.handle_callback(authorization_response, redirect_uri)

        print(f"DEBUG - Credentials obtained: {creds is not None}")
        print(f"DEBUG - Token file should be at: {auth_service.token_file}")

        flash('Autenticação com Google realizada com sucesso!', 'success')
        return redirect(url_for('main.gestao_automatica'))
    except Exception as e:
        print(f"ERROR in google_callback: {str(e)}")
        traceback.print_exc()
        flash(f'Erro ao processar callback: {str(e)}', 'error')
        return redirect(url_for('main.gestao_automatica'))


@bp.route('/google/disconnect', methods=['POST'])
def google_disconnect():
    """Disconnect Google account"""
    from app.services.google_auth_service import GoogleAuthService

    try:
        auth_service = GoogleAuthService()
        auth_service.revoke_authentication()
        flash('Desconectado do Google com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao desconectar: {str(e)}', 'error')

    return redirect(url_for('main.gestao_automatica'))


@bp.route('/automation/create/<int:evento_id>', methods=['POST'])
def create_event_automation(evento_id):
    """Create Google Form and Sheet for event"""
    from app.services.google_forms_service import GoogleFormsService

    try:
        evento = Event.query.get_or_404(evento_id)

        # Check if automation already exists
        if evento.google_form_id:
            flash('Este evento já tem automação configurada', 'warning')
            return redirect(url_for('main.gestao_automatica'))

        # Create form
        forms_service = GoogleFormsService()
        result = forms_service.create_event_form(evento)

        # Update event with form data
        evento.google_form_id = result['form_id']
        evento.google_form_url = result['form_url']
        evento.google_sheet_id = result['sheet_id']
        evento.google_sheet_url = result['sheet_url']

        db.session.commit()

        flash(f'✓ Google Form criado com sucesso!', 'success')
        flash(f'📋 Aceda ao formulário: {result["form_url"]}', 'info')

        return redirect(url_for('main.gestao_automatica'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao criar automação: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('main.gestao_automatica'))


@bp.route('/automation/sync/<int:evento_id>', methods=['POST'])
def sync_event_responses(evento_id):
    """Sync responses from Google Forms/Sheets"""
    from app.services.google_forms_service import GoogleFormsService

    try:
        evento = Event.query.get_or_404(evento_id)

        if not evento.google_form_id:
            flash('Este evento não tem formulário Google associado', 'error')
            return redirect(url_for('main.gestao_automatica'))

        # Get form responses
        forms_service = GoogleFormsService()
        responses = forms_service.get_form_responses(evento.google_form_id)

        # Sync participants
        new_participants = 0
        updated_participants = 0

        for response_data in responses:
            # Check if participant already exists
            existing = Participant.query.filter_by(
                evento_id=evento.id,
                email=response_data['email']
            ).first()

            if existing:
                # Update existing participant
                existing.nome = response_data['nome']
                existing.telefone = response_data['telefone']
                existing.empresa = response_data['empresa']
                existing.observacoes = response_data['observacoes']
                updated_participants += 1
            else:
                # Create new participant
                participante = Participant(
                    evento_id=evento.id,
                    nome=response_data['nome'],
                    email=response_data['email'],
                    telefone=response_data['telefone'],
                    empresa=response_data['empresa'],
                    observacoes=response_data['observacoes']
                )
                db.session.add(participante)
                new_participants += 1

        db.session.commit()

        flash(f'✓ Sincronização concluída: {new_participants} novos, {updated_participants} atualizados', 'success')
        return redirect(url_for('main.gestao_automatica'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao sincronizar: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('main.gestao_automatica'))


@bp.route('/automation/list-forms')
def list_google_forms():
    """List available Google Forms from Drive"""
    from app.services.google_forms_service import GoogleFormsService

    try:
        # Get limit from query parameter, default 100
        limit = request.args.get('limit', 100, type=int)
        limit = min(limit, 500)  # Cap at 500 for performance

        forms_service = GoogleFormsService()
        forms = forms_service.list_recent_forms(limit=limit)

        print(f"DEBUG - Returning {len(forms)} forms to frontend")

        return jsonify({
            'success': True,
            'forms': forms,
            'count': len(forms)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/automation/search-forms')
def search_google_forms():
    """Search Google Forms by name"""
    from app.services.google_forms_service import GoogleFormsService

    try:
        search_term = request.args.get('q', '')
        if not search_term:
            return jsonify({
                'success': False,
                'error': 'Search term required'
            }), 400

        forms_service = GoogleFormsService()
        forms = forms_service.search_forms_by_name(search_term, limit=20)

        return jsonify({
            'success': True,
            'forms': forms,
            'count': len(forms)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/automation/link/<int:evento_id>/<form_id>', methods=['POST'])
def link_existing_form(evento_id, form_id):
    """Link an existing Google Form to an event"""
    from app.services.google_forms_service import GoogleFormsService

    try:
        evento = Event.query.get_or_404(evento_id)

        # Check if event already has a form
        if evento.google_form_id:
            flash('Este evento já tem um formulário associado', 'warning')
            return redirect(url_for('main.gestao_automatica'))

        # Get form info
        forms_service = GoogleFormsService()
        form_info = forms_service.get_form_info(form_id)

        if not form_info:
            flash('Formulário não encontrado', 'error')
            return redirect(url_for('main.gestao_automatica'))

        # Link form to event
        evento.google_form_id = form_id
        evento.google_form_url = form_info['url']

        db.session.commit()

        flash(f'✓ Formulário "{form_info["title"]}" associado ao evento!', 'success')
        return redirect(url_for('main.gestao_automatica'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao associar formulário: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('main.gestao_automatica'))


# Certificate routes - Frontend wrappers for API endpoints
@bp.route('/certificado/gerar/<int:participante_id>', methods=['POST'])
def gerar_certificado(participante_id):
    """Generate certificate for single participant"""
    from app.services.certificate_service import CertificateService

    try:
        participante = Participant.query.get_or_404(participante_id)

        # Generate certificate
        cert_service = CertificateService()
        cert_path = cert_service.generate_certificate(participante_id)

        flash(f'✓ Certificado gerado para {participante.nome}!', 'success')
        return redirect(url_for('main.detalhe_evento', id=participante.evento_id))

    except Exception as e:
        flash(f'Erro ao gerar certificado: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(request.referrer or url_for('main.eventos'))


@bp.route('/certificado/enviar/<int:participante_id>', methods=['POST'])
def enviar_certificado(participante_id):
    """Send certificate via email"""
    try:
        participante = Participant.query.get_or_404(participante_id)

        if not participante.certificado_gerado:
            flash('Certificado ainda não foi gerado', 'error')
            return redirect(url_for('main.detalhe_evento', id=participante.evento_id))

        if not participante.certificado_path:
            flash('Caminho do certificado não encontrado', 'error')
            return redirect(url_for('main.detalhe_evento', id=participante.evento_id))

        # Send email with certificate
        from app.services.email_service import EmailService
        # Get event organization
        organizacao = participante.evento.organizacao
        email_service = EmailService(organization=organizacao)

        success = email_service.send_certificate(
            recipient_email=participante.email,
            recipient_name=participante.nome,
            event_name=participante.evento.nome,
            certificate_path=participante.certificado_path
        )

        if success:
            # Mark as sent
            from datetime import datetime
            participante.certificado_enviado = True
            participante.data_envio_certificado = datetime.utcnow()
            db.session.commit()

            flash(f'✓ Certificado enviado para {participante.email}!', 'success')
        else:
            flash(f'⚠️ Erro ao enviar certificado para {participante.email}', 'error')

        return redirect(url_for('main.detalhe_evento', id=participante.evento_id))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao enviar certificado: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(request.referrer or url_for('main.eventos'))


@bp.route('/certificado/gerar_todos/<int:evento_id>', methods=['POST'])
def gerar_certificados_todos(evento_id):
    """Generate certificates for all event participants"""
    from app.services.certificate_service import CertificateService

    try:
        evento = Event.query.get_or_404(evento_id)

        # Generate all certificates
        cert_service = CertificateService()
        result = cert_service.batch_generate_certificates(evento_id)

        if result['errors'] > 0:
            flash(f'⚠️ {result["generated"]} certificados gerados, {result["errors"]} erros', 'warning')
        else:
            flash(f'✓ {result["generated"]} certificados gerados com sucesso!', 'success')

        return redirect(url_for('main.detalhe_evento', id=evento_id))

    except Exception as e:
        flash(f'Erro ao gerar certificados: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(request.referrer or url_for('main.eventos'))


@bp.route('/certificado/enviar_todos/<int:evento_id>', methods=['POST'])
def enviar_certificados_todos(evento_id):
    """Send certificates to all event participants"""
    try:
        evento = Event.query.get_or_404(evento_id)

        # Get participants with generated certificates
        participantes = Participant.query.filter_by(
            evento_id=evento_id,
            certificado_gerado=True,
            certificado_enviado=False
        ).filter(Participant.deleted_at.is_(None)).all()

        if not participantes:
            flash('Nenhum certificado para enviar', 'warning')
            return redirect(url_for('main.detalhe_evento', id=evento_id))

        # Prepare recipients list
        recipients = []
        for p in participantes:
            if p.certificado_path:
                recipients.append({
                    'email': p.email,
                    'name': p.nome,
                    'event_name': evento.nome,
                    'certificate_path': p.certificado_path
                })

        # Send emails
        from app.services.email_service import EmailService
        # Get event organization
        organizacao = evento.organizacao
        email_service = EmailService(organization=organizacao)
        result = email_service.send_bulk_certificates(recipients)

        # Mark sent certificates
        from datetime import datetime
        for participante in participantes:
            if participante.certificado_path:
                participante.certificado_enviado = True
                participante.data_envio_certificado = datetime.utcnow()

        db.session.commit()

        if result['failed'] > 0:
            flash(f'⚠️ {result["sent"]} enviados, {result["failed"]} falharam', 'warning')
        else:
            flash(f'✓ {result["sent"]} certificados enviados com sucesso!', 'success')

        return redirect(url_for('main.detalhe_evento', id=evento_id))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao enviar certificados: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(request.referrer or url_for('main.eventos'))


@bp.route('/certificado/download/<int:participante_id>', methods=['GET'])
def download_certificado(participante_id):
    """Download generated certificate PDF"""
    try:
        participante = Participant.query.get_or_404(participante_id)

        if not participante.certificado_gerado or not participante.certificado_path:
            flash('Certificado não encontrado ou ainda não foi gerado', 'error')
            return redirect(url_for('main.detalhe_evento', id=participante.evento_id))

        # Check if file exists
        import os
        if not os.path.exists(participante.certificado_path):
            flash('Arquivo de certificado não encontrado', 'error')
            return redirect(url_for('main.detalhe_evento', id=participante.evento_id))

        # Send file for download
        from flask import send_file
        return send_file(
            participante.certificado_path,
            as_attachment=True,
            download_name=f'Certificado_{participante.nome.replace(" ", "_")}.pdf',
            mimetype='application/pdf'
        )

    except Exception as e:
        flash(f'Erro ao fazer download do certificado: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(request.referrer or url_for('main.eventos'))


@bp.route('/remover_participante/<int:evento_id>/<int:participante_id>', methods=['POST'])
def remover_participante(evento_id, participante_id):
    """Soft delete participant"""
    try:
        participante = Participant.query.get_or_404(participante_id)

        from datetime import datetime
        participante.deleted_at = datetime.utcnow()
        db.session.commit()

        flash(f'✓ Participante removido com sucesso!', 'success')
        return redirect(url_for('main.detalhe_evento', id=evento_id))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover participante: {str(e)}', 'error')
        return redirect(url_for('main.detalhe_evento', id=evento_id))


@bp.route('/adicionar_participante/<int:evento_id>', methods=['GET', 'POST'])
def adicionar_participante(evento_id):
    """Add participant manually to event"""
    evento = Event.query.get_or_404(evento_id)

    if request.method == 'POST':
        try:
            email = request.form.get('email', '')

            # Check if participant already exists (including soft-deleted)
            existing = Participant.query.filter_by(
                evento_id=evento_id,
                email=email
            ).first()

            if existing:
                if existing.deleted_at:
                    # Reactivate soft-deleted participant
                    from datetime import datetime
                    existing.nome = request.form.get('nome', '')
                    existing.telefone = request.form.get('telefone', '')
                    existing.empresa = request.form.get('empresa', '')
                    existing.observacoes = request.form.get('observacoes', '')
                    existing.deleted_at = None
                    existing.updated_at = datetime.utcnow()
                    db.session.commit()
                    flash(f'✓ Participante {existing.nome} reativado com sucesso!', 'success')
                else:
                    flash(f'⚠️ Participante com email {email} já existe neste evento!', 'warning')
                return redirect(url_for('main.detalhe_evento', id=evento_id))

            # Create new participant
            participante = Participant(
                evento_id=evento_id,
                nome=request.form.get('nome', ''),
                email=email,
                telefone=request.form.get('telefone', ''),
                empresa=request.form.get('empresa', ''),
                observacoes=request.form.get('observacoes', '')
            )
            db.session.add(participante)
            db.session.commit()

            flash(f'✓ Participante {participante.nome} adicionado com sucesso!', 'success')
            return redirect(url_for('main.detalhe_evento', id=evento_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao adicionar participante: {str(e)}', 'error')
            import traceback
            traceback.print_exc()

    return render_template('adicionar_participante.html', evento=evento)


@bp.route('/editar_participante/<int:participante_id>', methods=['GET', 'POST'])
def editar_participante(participante_id):
    """Edit participant details and status"""
    participante = Participant.query.get_or_404(participante_id)

    if request.method == 'POST':
        try:
            participante.nome = request.form.get('nome', '')
            participante.email = request.form.get('email', '')
            participante.status = request.form.get('status', 'pendente')
            participante.telefone = request.form.get('telefone', '')
            participante.empresa = request.form.get('empresa', '')

            db.session.commit()

            flash(f'✓ Participante {participante.nome} atualizado com sucesso!', 'success')
            return redirect(url_for('main.detalhe_evento', id=participante.evento_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar participante: {str(e)}', 'error')
            import traceback
            traceback.print_exc()

    return render_template('editar_participante.html', participante=participante)


@bp.route('/validate/certificate/<int:participant_id>')
def validate_certificate(participant_id):
    """Validate certificate via QR code"""
    participante = Participant.query.get(participant_id)

    if not participante or participante.deleted_at:
        return render_template('validar_certificado.html',
                             valid=False,
                             message="Certificado não encontrado ou inválido")

    if not participante.certificado_gerado:
        return render_template('validar_certificado.html',
                             valid=False,
                             message="Certificado não foi gerado para este participante")

    evento = Event.query.get(participante.evento_id)
    if not evento or evento.deleted_at:
        return render_template('validar_certificado.html',
                             valid=False,
                             message="Evento não encontrado")

    # Certificate is valid
    return render_template('validar_certificado.html',
                         valid=True,
                         participante=participante,
                         evento=evento)


# Additional routes can be added here as needed
# These are the core routes for the beautiful frontend
