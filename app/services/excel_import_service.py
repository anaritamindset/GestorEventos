"""
Excel Import Service - Import events and participants from Excel files
"""

import pandas as pd
from datetime import datetime
from werkzeug.datastructures import FileStorage
import os


class ExcelImportService:
    """Service to import events and participants from Excel files"""

    def __init__(self):
        self.supported_extensions = ['.xlsx', '.xls']

    def validate_file(self, file: FileStorage) -> tuple[bool, str]:
        """Validate uploaded Excel file"""
        if not file:
            return False, "Nenhum ficheiro foi enviado"

        filename = file.filename
        if not any(filename.endswith(ext) for ext in self.supported_extensions):
            return False, f"Formato inválido. Use {', '.join(self.supported_extensions)}"

        return True, "Ficheiro válido"

    def parse_excel_file(self, file_path: str) -> dict:
        """
        Parse Excel file and extract event and participants data

        Supports multiple formats:
        1. Multiple events: Each sheet is a complete event (event info at top, participants below)
        2. Two-sheet format: Sheet 1 = event info, Sheet 2 = participants
        3. Single sheet: Event info at top, participants below
        """
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            sheets = excel_file.sheet_names

            # Check if this is a multi-event file (each sheet is one complete event)
            # or the old format (separate sheets for info and participants)
            if len(sheets) >= 2:
                # Try to detect format by checking first sheet
                first_sheet = pd.read_excel(excel_file, sheet_name=0, header=None)

                # If first sheet has participant data (look for "Nome" + "Email" in same row)
                # then it's multi-event format (each sheet = one event)
                has_participant_section = self._find_participant_section(first_sheet) is not None

                if has_participant_section:
                    # Multi-event format: each sheet is one complete event
                    return self._parse_multi_event_format(excel_file)
                else:
                    # Two sheet format (old): sheet 1 = event, sheet 2 = participants
                    return self._parse_two_sheet_format(excel_file)
            else:
                # Single sheet format
                return self._parse_single_sheet_format(excel_file)

        except Exception as e:
            raise Exception(f"Erro ao processar Excel: {str(e)}")

    def _parse_multi_event_format(self, excel_file: pd.ExcelFile) -> dict:
        """Parse Excel with multiple events - each sheet is one complete event"""
        events = []

        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)

            # Find where participant list starts
            participant_start_row = self._find_participant_section(df)

            if participant_start_row is not None:
                # Event data is above participant section
                # BUT also check first 3 rows of participant section for event data in columns 2-3
                event_df = df.iloc[:participant_start_row]

                # For format where event info is in columns 2-3 of first rows
                # Include first 3 rows to extract event data from right columns
                event_df_extended = df.iloc[:min(participant_start_row + 3, len(df))]

                # Participant data starts after
                participants_df = df.iloc[participant_start_row:]
            else:
                # No participants found, all data is event info
                event_df_extended = df
                participants_df = pd.DataFrame()

            event_data = self._extract_event_data(event_df_extended)
            participants_data = self._extract_participants_data(participants_df)

            events.append({
                'event': event_data,
                'participants': participants_data
            })

        # Return all events
        return {'events': events}

    def _parse_two_sheet_format(self, excel_file: pd.ExcelFile) -> dict:
        """Parse Excel with separate sheets for event and participants"""
        # Read first sheet for event info (no header, it's key-value pairs)
        event_df = pd.read_excel(excel_file, sheet_name=0, header=None)

        # Read second sheet for participants
        participants_df = pd.read_excel(excel_file, sheet_name=1)

        # Extract event data (assume first row or key-value pairs)
        event_data = self._extract_event_data(event_df)

        # Extract participants
        participants_data = self._extract_participants_data(participants_df)

        return {
            'event': event_data,
            'participants': participants_data
        }

    def _parse_single_sheet_format(self, excel_file: pd.ExcelFile) -> dict:
        """Parse Excel with event info at top and participants below"""
        df = pd.read_excel(excel_file, sheet_name=0)

        # Try to find where participant list starts
        participant_start_row = self._find_participant_section(df)

        if participant_start_row is not None:
            # Event data is above participant section
            event_df = df.iloc[:participant_start_row]
            # Participant data starts after
            participants_df = df.iloc[participant_start_row:]
        else:
            # Assume all is participant data if no event section found
            event_df = pd.DataFrame()
            participants_df = df

        event_data = self._extract_event_data(event_df)
        participants_data = self._extract_participants_data(participants_df)

        return {
            'event': event_data,
            'participants': participants_data
        }

    def _find_participant_section(self, df: pd.DataFrame) -> int:
        """Find row where participant list starts (header row with multiple columns)"""
        # Look for rows with multiple common column headers in the same row
        # This indicates a table header, not just a single "Nome" field

        for idx, row in df.iterrows():
            # Count how many participant-related headers are in this row
            row_lower = [str(cell).lower().strip() for cell in row if pd.notna(cell)]

            # Check if this looks like a header row (has multiple expected columns)
            has_nome = any('nome' in cell or 'name' in cell for cell in row_lower)
            has_email = any('email' in cell or 'e-mail' in cell or 'mail' in cell for cell in row_lower)
            has_telefone = any('telefone' in cell or 'phone' in cell or 'tel' in cell for cell in row_lower)

            # If we have at least 2 of these common headers in same row, it's probably the participant section
            header_count = sum([has_nome, has_email, has_telefone])
            if header_count >= 2:
                return idx

        return None

    def _extract_event_data(self, df: pd.DataFrame) -> dict:
        """Extract event data from dataframe"""
        event_data = {
            'nome': '',
            'data': None,
            'data_inicio': None,
            'data_fim': None,
            'duracao': 60,
            'descricao': '',
            'formadora': '',
            'local': ''
        }

        if df.empty:
            return event_data

        # Try key-value format in columns 0-1 OR 2-3
        if len(df.columns) >= 2:
            for _, row in df.iterrows():
                # Try standard format (columns 0-1)
                key = str(row.iloc[0]).strip().lower() if pd.notna(row.iloc[0]) else ''
                value = row.iloc[1] if pd.notna(row.iloc[1]) else ''

                # Also try alternative format (columns 2-3) for formats where event data is in right columns
                if len(df.columns) >= 4:
                    key2 = str(row.iloc[2]).strip().lower() if pd.notna(row.iloc[2]) else ''
                    value2 = row.iloc[3] if pd.notna(row.iloc[3]) else ''

                    # Use columns 2-3 if they have event-related keys
                    if any(keyword in key2 for keyword in ['nome', 'data', 'duração', 'duracao', 'local', 'formador']):
                        key = key2
                        value = value2

                if 'nome' in key or 'event' in key or 'título' in key:
                    if not event_data['nome'] and value:  # Only set if not already set
                        event_data['nome'] = str(value).strip()
                elif 'data' in key and 'fim' not in key and 'inicio' not in key:
                    if not event_data['data'] and value:
                        event_data['data'] = self._parse_date(value)
                elif 'data' in key and 'inicio' in key:
                    if not event_data['data_inicio'] and value:
                        event_data['data_inicio'] = self._parse_date(value)
                elif 'data' in key and 'fim' in key:
                    if not event_data['data_fim'] and value:
                        event_data['data_fim'] = self._parse_date(value)
                elif 'duração' in key or 'duracao' in key or 'duration' in key:
                    if event_data['duracao'] == 60 and value:  # Only set if still default
                        event_data['duracao'] = self._parse_duration(value)
                elif 'descrição' in key or 'descricao' in key or 'description' in key:
                    if not event_data['descricao'] and value:
                        event_data['descricao'] = str(value).strip()
                elif 'formador' in key or 'facilitador' in key or 'trainer' in key:
                    if not event_data['formadora'] and value:
                        event_data['formadora'] = str(value).strip()
                elif 'local' in key or 'location' in key:
                    if not event_data['local'] and value:
                        event_data['local'] = str(value).strip()

        return event_data

    def _extract_participants_data(self, df: pd.DataFrame) -> list:
        """Extract participants data from dataframe"""
        participants = []

        if df.empty:
            return participants

        # Clean dataframe - remove empty rows
        df = df.dropna(how='all')

        if df.empty:
            return participants

        # Reset index after cleaning
        df = df.reset_index(drop=True)

        # Detect header row (first row with multiple non-empty values)
        header_row = 0
        for idx, row in df.iterrows():
            non_empty = row.notna().sum()
            if non_empty >= 2:  # At least 2 columns with data
                header_row = idx
                break

        # Check if we have enough rows for header + data
        if header_row >= len(df):
            return participants

        # Use detected header row
        df.columns = df.iloc[header_row].values
        df = df.iloc[header_row + 1:]

        # Check if we have data rows
        if df.empty:
            return participants

        # Map common column names
        column_mapping = {
            'nome': ['nome', 'name', 'participante', 'participant'],
            'email': ['email', 'e-mail', 'mail'],
            'telefone': ['telefone', 'phone', 'telemóvel', 'telemovel', 'contacto'],
            'empresa': ['empresa', 'company', 'organization', 'organização'],
            'observacoes': ['observações', 'observacoes', 'notes', 'notas', 'comments']
        }

        # Find actual column names
        actual_columns = {}
        for target_col, possible_names in column_mapping.items():
            for col in df.columns:
                col_str = str(col).lower().strip()
                if any(name in col_str for name in possible_names):
                    actual_columns[target_col] = col
                    break

        # Extract participants
        for _, row in df.iterrows():
            participant = {}

            # Skip rows with no name
            if 'nome' in actual_columns:
                nome = row.get(actual_columns['nome'], '')
                if pd.isna(nome) or str(nome).strip() == '':
                    continue
                participant['nome'] = str(nome).strip()
            else:
                # Try first non-empty column as name
                for val in row:
                    if pd.notna(val) and str(val).strip():
                        participant['nome'] = str(val).strip()
                        break
                if 'nome' not in participant:
                    continue

            # Extract other fields
            for field, col in actual_columns.items():
                if field == 'nome':
                    continue
                value = row.get(col, '')
                if pd.notna(value):
                    participant[field] = str(value).strip()

            participants.append(participant)

        return participants

    def _parse_date(self, value) -> datetime:
        """Parse date from various formats"""
        if pd.isna(value):
            return None

        if isinstance(value, datetime):
            return value

        value_str = str(value).strip()

        # Try Portuguese format first: "29 de dezembro de 2025"
        portuguese_months = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
            'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
        }

        # Check if it's Portuguese format
        if ' de ' in value_str.lower():
            try:
                parts = value_str.lower().split(' de ')
                if len(parts) == 3:
                    day = int(parts[0].strip())
                    month_name = parts[1].strip()
                    year = int(parts[2].strip())

                    if month_name in portuguese_months:
                        month = portuguese_months[month_name]
                        return datetime(year, month, day)
            except:
                pass

        # Try common date formats (try 2-digit year first, then 4-digit)
        date_formats = [
            '%d/%m/%y',      # DD/MM/YY (e.g., 15/01/26)
            '%d-%m-%y',      # DD-MM-YY
            '%d/%m/%Y',      # DD/MM/YYYY
            '%d-%m-%Y',      # DD-MM-YYYY
            '%Y-%m-%d',      # YYYY-MM-DD
            '%d/%m/%Y %H:%M',
            '%d-%m-%Y %H:%M',
            '%d/%m/%y %H:%M',
            '%d-%m-%y %H:%M'
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(value_str, fmt)
            except ValueError:
                continue

        # If all fail, return None
        return None

    def _parse_duration(self, value) -> int:
        """Parse duration in minutes"""
        if pd.isna(value):
            return 60

        try:
            value_str = str(value).strip().lower()

            # Check for format like "1h40" or "2h30"
            if 'h' in value_str:
                parts = value_str.split('h')
                hours = int(parts[0]) if parts[0].isdigit() else 0
                minutes = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                return hours * 60 + minutes

            # Try to extract number
            numeric = ''.join(c for c in value_str if c.isdigit() or c == '.')
            return int(float(numeric)) if numeric else 60
        except:
            return 60

    def save_uploaded_file(self, file: FileStorage, upload_folder: str) -> str:
        """Save uploaded file temporarily"""
        os.makedirs(upload_folder, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"upload_{timestamp}_{file.filename}"
        filepath = os.path.join(upload_folder, filename)

        file.save(filepath)
        return filepath
