from flask import Blueprint, request, jsonify
from app.services import GoogleService
from app import db
from app.models import Event, Participant
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('gdrive', __name__, url_prefix='/api/gdrive')

# Initialize Google Service (lazy loading or on first request recommended, but for now global is fine if handled carefully)
# We instantiate it here, but authentication happens when methods are called
google_service = GoogleService() 

@bp.route('/auth', methods=['GET'])
def authenticate():
    """Trigger authentication flow"""
    try:
        google_service.authenticate()
        return jsonify({'message': 'Authenticated successfully'}), 200
    except Exception as e:
        logger.error(f"Auth error: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/files', methods=['GET'])
def list_files():
    """List spreadsheet files"""
    try:
        files = google_service.list_spreadsheets()
        return jsonify({'files': files}), 200
    except Exception as e:
        logger.error(f"List files error: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/preview/<spreadsheet_id>', methods=['GET'])
def preview_sheet(spreadsheet_id):
    """Preview data from spreadsheet to validate format"""
    try:
        # Read first few rows to try to identify event info
        data = google_service.get_spreadsheet_data(spreadsheet_id, 'A1:E20')
        metadata = google_service.get_spreadsheet_metadata(spreadsheet_id)
        
        return jsonify({
            'metadata': metadata,
            'preview': data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/import', methods=['POST'])
def import_event():
    """Import event and participants from Sheet"""
    try:
        data = request.get_json()
        spreadsheet_id = data.get('spreadsheet_id')

        if not spreadsheet_id:
            return jsonify({'error': 'Spreadsheet ID required'}), 400

        # Read full data
        # Assumption: First few rows are metadata, then a header row, then participants
        # We need a smarter parser here, but starting with a convention:
        # Row 1-5: Key-Value pairs for Event basics (Nome, Data, etc)
        # Row 6+: Header and Participants

        raw_values = google_service.get_spreadsheet_data(spreadsheet_id)

        parsed_event = {
            'nome': 'Evento Importado',
            'participantes': []
        }

        participants_start_row = 0

        # Simple heuristic parser
        for i, row in enumerate(raw_values):
            if not row: continue

            # Check for Event Metadata
            first_cell = row[0].lower().strip()
            if 'título' in first_cell or 'evento' in first_cell:
                if len(row) > 1: parsed_event['nome'] = row[1]
            elif 'data' in first_cell:
                if len(row) > 1: parsed_event['data_inicio'] = row[1]
            elif 'duração' in first_cell:
                 if len(row) > 1: parsed_event['duracao'] = row[1]

            # Check for Participants Header
            if 'nome' in first_cell and ('email' in row or 'e-mail' in row or 'correio' in row):
                participants_start_row = i + 1
                # Identify column indices
                try:
                    name_idx = next(idx for idx, cell in enumerate(row) if 'nome' in cell.lower())
                    email_idx = next(idx for idx, cell in enumerate(row) if 'email' in cell.lower() or 'correio' in cell.lower())

                    parsed_event['indices'] = {'name': name_idx, 'email': email_idx}
                except StopIteration:
                     pass # Fallback needed
                break

        # Extract Participants
        if 'indices' in parsed_event and participants_start_row > 0:
            name_idx = parsed_event['indices']['name']
            email_idx = parsed_event['indices']['email']

            for row in raw_values[participants_start_row:]:
                if len(row) > max(name_idx, email_idx):
                    p_name = row[name_idx].strip()
                    p_email = row[email_idx].strip()
                    if p_name and p_email:
                        parsed_event['participantes'].append({
                            'nome': p_name,
                            'email': p_email,
                            'status': 'pendente'
                        })

        return jsonify({# Return the parsed structure for confirmation before saving
            'parsed_event': parsed_event,
            'original_data_count': len(raw_values)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/import/participants/<int:event_id>', methods=['POST'])
def import_participants_to_event(event_id):
    """Import participants from Google Sheet to existing event"""
    try:
        # Verify event exists
        event = Event.query.get_or_404(event_id)
        if event.deleted_at:
            return jsonify({'error': 'Evento não encontrado'}), 404

        data = request.get_json()
        spreadsheet_id = data.get('spreadsheet_id')
        sheet_range = data.get('range', 'A2:Z1000')  # Default: skip header row
        skip_duplicates = data.get('skip_duplicates', True)

        if not spreadsheet_id:
            return jsonify({'error': 'Spreadsheet ID required'}), 400

        # Column mapping (can be customized by frontend)
        column_mapping = data.get('column_mapping', {
            0: 'nome',
            1: 'email',
            2: 'telefone',
            3: 'empresa',
            4: 'observacoes'
        })
        # Convert string keys to int
        column_mapping = {int(k): v for k, v in column_mapping.items()}

        # Read data from sheet
        raw_values = google_service.get_spreadsheet_data(spreadsheet_id, sheet_range)

        stats = {
            'total_rows': len(raw_values),
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'error_details': []
        }

        for idx, row in enumerate(raw_values, start=2):  # Start at 2 (1 is header)
            try:
                # Extract data based on column mapping
                participant_data = {}
                for col_idx, field_name in column_mapping.items():
                    if col_idx < len(row):
                        value = row[col_idx].strip() if row[col_idx] else None
                        if value:
                            participant_data[field_name] = value

                # Validate required fields
                if 'nome' not in participant_data or 'email' not in participant_data:
                    stats['skipped'] += 1
                    stats['error_details'].append({
                        'row': idx,
                        'error': 'Nome ou email em falta',
                        'data': row[:5]  # Only first 5 columns for privacy
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
                    'data': row[:5] if row else []
                })
                logger.error(f"Erro ao importar linha {idx}: {e}")
                db.session.rollback()

        return jsonify({
            'message': f'Importação concluída: {stats["imported"]} participantes importados',
            'stats': stats
        }), 200

    except Exception as e:
        logger.error(f"Import error: {e}")
        return jsonify({'error': str(e)}), 500
