#!/usr/bin/env python3
"""
Template Manager untuk Sistem Laporan FFB
Mengelola template laporan dan konfigurasi yang digunakan untuk generating laporan
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

class TemplateManager:
    """Manager untuk template laporan FFB"""

    def __init__(self, templates_dir: str = "templates"):
        # Resolve to absolute path - templates is in the same directory as this script's parent
        if not os.path.isabs(templates_dir):
            # Get the parent directory of src (which is Reporting_System_Ifes)
            current_file = os.path.abspath(__file__)
            src_dir = os.path.dirname(current_file)
            # templates is in the same level as src, not parent of src
            templates_dir = os.path.join(src_dir, "..", templates_dir)
            # Resolve .. to get absolute path
            templates_dir = os.path.abspath(templates_dir)

        self.templates_dir = templates_dir
        self.templates: Dict[str, Dict] = {}
        self.logger = logging.getLogger(__name__)

        # Debug logging
        self.logger.info(f"TemplateManager initialized with directory: {self.templates_dir}")

        self._load_templates()

    def _load_templates(self):
        """Load semua template dari directory"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            self.logger.warning(f"Created templates directory: {self.templates_dir}")

        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.templates_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        template = json.load(f)
                        template_id = template.get('template_id')
                        if template_id:
                            self.templates[template_id] = template
                            self.logger.info(f"Loaded template: {template_id}")
                        else:
                            self.logger.warning(f"Template {filename} missing template_id")
                except Exception as e:
                    self.logger.error(f"Error loading template {filename}: {e}")

    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get template berdasarkan ID"""
        return self.templates.get(template_id)

    def get_all_templates(self) -> List[Dict]:
        """Get semua template yang tersedia"""
        return list(self.templates.values())

    def get_templates_by_category(self, category: str) -> List[Dict]:
        """Get template berdasarkan kategori"""
        return [t for t in self.templates.values() if t.get('category') == category]

    def save_template(self, template: Dict) -> bool:
        """Save template ke file"""
        try:
            template_id = template.get('template_id')
            if not template_id:
                raise ValueError("Template must have template_id")

            # Update created_date if new template
            if template_id not in self.templates:
                template['created_date'] = datetime.now().strftime('%Y-%m-%d')
                template['created_by'] = 'user'

            template['updated_date'] = datetime.now().strftime('%Y-%m-%d')

            filename = f"{template_id}.json"
            filepath = os.path.join(self.templates_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=4, ensure_ascii=False)

            self.templates[template_id] = template
            self.logger.info(f"Saved template: {template_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving template: {e}")
            return False

    def delete_template(self, template_id: str) -> bool:
        """Delete template"""
        try:
            if template_id in self.templates:
                filename = f"{template_id}.json"
                filepath = os.path.join(self.templates_dir, filename)

                if os.path.exists(filepath):
                    os.remove(filepath)

                del self.templates[template_id]
                self.logger.info(f"Deleted template: {template_id}")
                return True
            else:
                self.logger.warning(f"Template not found: {template_id}")
                return False

        except Exception as e:
            self.logger.error(f"Error deleting template: {e}")
            return False

    def validate_template(self, template: Dict) -> List[str]:
        """Validasi template structure"""
        errors = []

        # Required fields
        required_fields = ['template_id', 'name', 'description', 'category',
                          'version', 'parameters', 'report_structure']

        for field in required_fields:
            if field not in template:
                errors.append(f"Missing required field: {field}")

        # Validate parameters
        if 'parameters' in template:
            for i, param in enumerate(template['parameters']):
                if not isinstance(param, dict):
                    errors.append(f"Parameter {i} must be a dictionary")
                    continue

                param_required = ['name', 'type', 'display_name', 'description', 'ui_component']
                for field in param_required:
                    if field not in param:
                        errors.append(f"Parameter {i} missing field: {field}")

        # Validate report structure
        if 'report_structure' in template:
            if 'table_columns' not in template['report_structure']:
                errors.append("Missing table_columns in report_structure")
            else:
                for i, col in enumerate(template['report_structure']['table_columns']):
                    col_required = ['name', 'title', 'width', 'alignment']
                    for field in col_required:
                        if field not in col:
                            errors.append(f"Table column {i} missing field: {field}")

        return errors

    def get_parameter_values(self, template_id: str) -> Dict:
        """Get default values untuk parameter template"""
        template = self.get_template(template_id)
        if not template:
            return {}

        values = {}
        for param in template.get('parameters', []):
            param_name = param['name']
            if 'default_value' in param:
                values[param_name] = param['default_value']
            elif param['type'] == 'BOOLEAN':
                values[param_name] = False
            elif param['type'] == 'MULTI_SELECT':
                values[param_name] = []
            else:
                values[param_name] = None

        return values

    def get_template_choices(self) -> List[str]:
        """Get list of template choices for UI"""
        choices = []
        for template in self.templates.values():
            display_text = f"{template.get('name', 'Unknown')} - {template.get('category', 'Unknown')}"
            choices.append((template['template_id'], display_text))
        return sorted(choices, key=lambda x: x[1])

    def generate_report_data(self, template_id: str, parameters: Dict, analysis_data: Dict) -> Dict:
        """Generate report data berdasarkan template dan hasil analysis"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        report_data = {
            'template': template,
            'parameters': parameters,
            'generated_at': datetime.now(),
            'data': analysis_data
        }

        # Apply template styling and structure
        report_structure = template.get('report_structure', {})

        # Format dates
        if 'START_DATE' in parameters:
            start_date = parameters['START_DATE']
            if hasattr(start_date, 'strftime'):
                report_data['formatted_start_date'] = start_date.strftime('%d %B %Y')
            else:
                report_data['formatted_start_date'] = str(start_date)

        if 'END_DATE' in parameters:
            end_date = parameters['END_DATE']
            if hasattr(end_date, 'strftime'):
                report_data['formatted_end_date'] = end_date.strftime('%d %B %Y')
            else:
                report_data['formatted_end_date'] = str(end_date)

        # Generate filename
        period = f"{parameters.get('START_DATE', 'unknown')}_to_{parameters.get('END_DATE', 'unknown')}"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_data['filename'] = f"Laporan_{template_id}_{period}_{timestamp}.pdf"

        return report_data