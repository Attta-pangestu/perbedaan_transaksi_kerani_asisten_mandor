"""
Template Loader
Sistem untuk memuat template verifikasi secara dinamis.
"""

import json
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional, Type, Union
import logging

from ..config.settings import Settings


class TemplateLoader:
    """
    Loader untuk template verifikasi yang dapat dikonfigurasi.
    Mendukung loading template dari file JSON dan class Python.
    """
    
    def __init__(self, templates_dir: Optional[Union[str, Path]] = None):
        """
        Initialize template loader.
        
        Args:
            templates_dir: Direktori template (opsional, default dari Settings)
        """
        self.settings = Settings()
        self.logger = logging.getLogger(__name__)
        
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            self.templates_dir = self.settings.TEMPLATES_DIR
        
        # Cache untuk template yang sudah dimuat
        self._template_cache = {}
        self._class_cache = {}
        
        # Registry template yang tersedia
        self._template_registry = {}
        
        # Scan template saat inisialisasi
        self._scan_templates()
    
    def _scan_templates(self):
        """
        Scan direktori template untuk menemukan template yang tersedia.
        """
        if not self.templates_dir.exists():
            self.logger.warning(f"Template directory tidak ditemukan: {self.templates_dir}")
            return
        
        # Scan file JSON
        json_files = list(self.templates_dir.glob("*.json"))
        for json_file in json_files:
            template_name = json_file.stem
            self._template_registry[template_name] = {
                'type': 'json',
                'path': json_file,
                'class_path': None
            }
        
        # Scan file Python
        py_files = list(self.templates_dir.glob("*.py"))
        for py_file in py_files:
            if py_file.name == "__init__.py":
                continue
                
            template_name = py_file.stem
            
            # Coba temukan class template
            class_name = self._get_template_class_name(template_name)
            
            if template_name in self._template_registry:
                # Update existing entry dengan class path
                self._template_registry[template_name]['class_path'] = f"templates.{template_name}.{class_name}"
            else:
                # Buat entry baru untuk Python-only template
                self._template_registry[template_name] = {
                    'type': 'python',
                    'path': py_file,
                    'class_path': f"templates.{template_name}.{class_name}"
                }
        
        self.logger.info(f"Ditemukan {len(self._template_registry)} template: {list(self._template_registry.keys())}")
    
    def _get_template_class_name(self, template_name: str) -> str:
        """
        Generate nama class berdasarkan nama template.
        
        Args:
            template_name: Nama template
        
        Returns:
            str: Nama class
        """
        # Convert snake_case ke PascalCase
        parts = template_name.split('_')
        class_name = ''.join(word.capitalize() for word in parts) + 'Template'
        return class_name
    
    def get_available_templates(self) -> List[str]:
        """
        Dapatkan daftar template yang tersedia.
        
        Returns:
            List: Daftar nama template
        """
        return list(self._template_registry.keys())
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Dapatkan informasi template.
        
        Args:
            template_name: Nama template
        
        Returns:
            Dict: Informasi template atau None jika tidak ditemukan
        """
        if template_name not in self._template_registry:
            return None
        
        registry_info = self._template_registry[template_name]
        
        # Load template config untuk mendapatkan info detail
        try:
            config = self.load_template_config(template_name)
            if config and 'template_info' in config:
                info = config['template_info'].copy()
                info.update({
                    'registry_type': registry_info['type'],
                    'config_path': str(registry_info['path']),
                    'class_path': registry_info.get('class_path')
                })
                return info
        except Exception as e:
            self.logger.error(f"Error loading template info for {template_name}: {e}")
        
        # Fallback ke registry info
        return {
            'name': template_name,
            'registry_type': registry_info['type'],
            'config_path': str(registry_info['path']),
            'class_path': registry_info.get('class_path')
        }
    
    def load_template_config(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Load konfigurasi template dari file JSON.
        
        Args:
            template_name: Nama template
        
        Returns:
            Dict: Konfigurasi template atau None jika tidak ditemukan
        """
        if template_name in self._template_cache:
            return self._template_cache[template_name]
        
        if template_name not in self._template_registry:
            self.logger.error(f"Template tidak ditemukan: {template_name}")
            return None
        
        registry_info = self._template_registry[template_name]
        
        # Untuk template JSON atau hybrid, load file JSON
        if registry_info['type'] in ['json', 'python'] and registry_info['path'].suffix == '.json':
            try:
                with open(registry_info['path'], 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self._template_cache[template_name] = config
                self.logger.info(f"Template config loaded: {template_name}")
                return config
                
            except Exception as e:
                self.logger.error(f"Error loading template config {template_name}: {e}")
                return None
        
        # Untuk Python-only template, coba load dari class
        elif registry_info['type'] == 'python':
            try:
                template_class = self.load_template_class(template_name)
                if template_class and hasattr(template_class, 'get_template_config'):
                    config = template_class.get_template_config()
                    self._template_cache[template_name] = config
                    return config
            except Exception as e:
                self.logger.error(f"Error loading Python template config {template_name}: {e}")
        
        return None
    
    def load_template_class(self, template_name: str) -> Optional[Type]:
        """
        Load class template Python.
        
        Args:
            template_name: Nama template
        
        Returns:
            Type: Class template atau None jika tidak ditemukan
        """
        if template_name in self._class_cache:
            return self._class_cache[template_name]
        
        if template_name not in self._template_registry:
            self.logger.error(f"Template tidak ditemukan: {template_name}")
            return None
        
        registry_info = self._template_registry[template_name]
        class_path = registry_info.get('class_path')
        
        if not class_path:
            self.logger.error(f"Class path tidak ditemukan untuk template: {template_name}")
            return None
        
        try:
            # Parse module dan class name
            module_path, class_name = class_path.rsplit('.', 1)
            
            # Import module relatif dari package verification_template_system
            full_module_path = f"verification_template_system.{module_path}"
            module = importlib.import_module(full_module_path)
            
            # Dapatkan class
            template_class = getattr(module, class_name)
            
            # Validasi bahwa ini adalah class template yang valid
            if not inspect.isclass(template_class):
                raise ValueError(f"{class_name} bukan class")
            
            self._class_cache[template_name] = template_class
            self.logger.info(f"Template class loaded: {template_name} -> {class_name}")
            return template_class
            
        except Exception as e:
            self.logger.error(f"Error loading template class {template_name}: {e}")
            return None
    
    def create_template_instance(self, template_name: str, **kwargs) -> Optional[Any]:
        """
        Buat instance template.
        
        Args:
            template_name: Nama template
            **kwargs: Parameter untuk constructor template
        
        Returns:
            Instance template atau None jika gagal
        """
        template_class = self.load_template_class(template_name)
        if not template_class:
            return None
        
        try:
            # Buat instance dengan parameter
            instance = template_class(**kwargs)
            self.logger.info(f"Template instance created: {template_name}")
            return instance
            
        except Exception as e:
            self.logger.error(f"Error creating template instance {template_name}: {e}")
            return None
    
    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """
        Validasi template untuk memastikan kelengkapan dan konsistensi.
        
        Args:
            template_name: Nama template
        
        Returns:
            Dict: Hasil validasi
        """
        result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        # Check registry
        if template_name not in self._template_registry:
            result['errors'].append(f"Template {template_name} tidak ditemukan di registry")
            return result
        
        registry_info = self._template_registry[template_name]
        result['info']['registry_type'] = registry_info['type']
        
        # Validasi file JSON jika ada
        if registry_info['path'].suffix == '.json':
            try:
                config = self.load_template_config(template_name)
                if not config:
                    result['errors'].append("Gagal memuat konfigurasi JSON")
                else:
                    # Validasi struktur JSON
                    required_sections = ['template_info', 'queries', 'business_logic']
                    for section in required_sections:
                        if section not in config:
                            result['errors'].append(f"Section '{section}' tidak ditemukan dalam konfigurasi")
                    
                    # Validasi template_info
                    if 'template_info' in config:
                        template_info = config['template_info']
                        required_fields = ['name', 'version', 'description']
                        for field in required_fields:
                            if field not in template_info:
                                result['warnings'].append(f"Field '{field}' tidak ditemukan dalam template_info")
                    
                    result['info']['config_sections'] = list(config.keys())
                    
            except Exception as e:
                result['errors'].append(f"Error validasi JSON: {e}")
        
        # Validasi class Python jika ada
        class_path = registry_info.get('class_path')
        if class_path:
            try:
                template_class = self.load_template_class(template_name)
                if not template_class:
                    result['errors'].append("Gagal memuat class template")
                else:
                    # Validasi method yang diperlukan
                    required_methods = ['connect_database', 'disconnect_database']
                    for method in required_methods:
                        if not hasattr(template_class, method):
                            result['warnings'].append(f"Method '{method}' tidak ditemukan dalam class")
                    
                    result['info']['class_name'] = template_class.__name__
                    result['info']['class_methods'] = [name for name, method in inspect.getmembers(template_class, predicate=inspect.isfunction)]
                    
            except Exception as e:
                result['errors'].append(f"Error validasi class: {e}")
        
        # Tentukan status valid
        result['valid'] = len(result['errors']) == 0
        
        return result
    
    def reload_templates(self):
        """
        Reload semua template (clear cache dan scan ulang).
        """
        self._template_cache.clear()
        self._class_cache.clear()
        self._template_registry.clear()
        
        self._scan_templates()
        self.logger.info("Template reloaded")
    
    def export_template_registry(self) -> Dict[str, Any]:
        """
        Export registry template untuk debugging atau dokumentasi.
        
        Returns:
            Dict: Registry template
        """
        export_data = {
            'templates_dir': str(self.templates_dir),
            'total_templates': len(self._template_registry),
            'templates': {}
        }
        
        for name, info in self._template_registry.items():
            template_info = self.get_template_info(name)
            validation = self.validate_template(name)
            
            export_data['templates'][name] = {
                'registry_info': info,
                'template_info': template_info,
                'validation': validation
            }
        
        return export_data


if __name__ == "__main__":
    # Test template loader
    print("=== Template Loader Test ===")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize loader
        loader = TemplateLoader()
        
        print(f"Templates directory: {loader.templates_dir}")
        print(f"Available templates: {loader.get_available_templates()}")
        
        # Test setiap template
        for template_name in loader.get_available_templates():
            print(f"\n--- Testing template: {template_name} ---")
            
            # Get info
            info = loader.get_template_info(template_name)
            if info:
                print(f"  Name: {info.get('name', 'N/A')}")
                print(f"  Version: {info.get('version', 'N/A')}")
                print(f"  Type: {info.get('registry_type', 'N/A')}")
            
            # Validate
            validation = loader.validate_template(template_name)
            print(f"  Valid: {validation['valid']}")
            if validation['errors']:
                print(f"  Errors: {validation['errors']}")
            if validation['warnings']:
                print(f"  Warnings: {validation['warnings']}")
            
            # Try load config
            try:
                config = loader.load_template_config(template_name)
                if config:
                    print(f"  Config sections: {list(config.keys())}")
            except Exception as e:
                print(f"  Config load error: {e}")
            
            # Try load class
            try:
                template_class = loader.load_template_class(template_name)
                if template_class:
                    print(f"  Class: {template_class.__name__}")
            except Exception as e:
                print(f"  Class load error: {e}")
        
        # Export registry
        print("\n--- Registry Export ---")
        registry = loader.export_template_registry()
        print(f"Total templates: {registry['total_templates']}")
        
        print("Template loader test completed!")
        
    except Exception as e:
        print(f"Template loader test failed: {e}")
        raise