"""
Configuration Management untuk FFB Scanner Analysis System

Modul ini mengatur semua konfigurasi sistem termasuk:
1. Database connections
2. Report settings
3. Analysis parameters
4. GUI configurations
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FFBConfig:
    """
    Central configuration manager untuk FFB Analysis System
    """

    def __init__(self, config_dir: str = None):
        """
        Initialize configuration

        Args:
            config_dir: Directory path untuk config files
        """
        if config_dir is None:
            # Default config directory
            self.config_dir = Path(__file__).parent / "config"
        else:
            self.config_dir = Path(config_dir)

        self.config_dir.mkdir(exist_ok=True)

        # Load configurations
        self.estate_config = self._load_estate_config()
        self.report_config = self._load_report_config()
        self.analysis_config = self._get_default_analysis_config()

    def _load_estate_config(self) -> Dict:
        """
        Load estate database configuration

        Returns:
            Dict dengan estate database paths
        """
        config_file = self.config_dir / "estate_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Loaded estate config from {config_file}")
                return config
            except Exception as e:
                logger.error(f"Error loading estate config: {e}")
                return self._get_default_estate_config()
        else:
            logger.info("Estate config file not found, using default")
            default_config = self._get_default_estate_config()
            self._save_estate_config(default_config)
            return default_config

    def _load_report_config(self) -> Dict:
        """
        Load report configuration

        Returns:
            Dict dengan report settings
        """
        config_file = self.config_dir / "report_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"Loaded report config from {config_file}")
                return config
            except Exception as e:
                logger.error(f"Error loading report config: {e}")
                return self._get_default_report_config()
        else:
            logger.info("Report config file not found, using default")
            default_config = self._get_default_report_config()
            self._save_report_config(default_config)
            return default_config

    def _get_default_estate_config(self) -> Dict:
        """
        Get default estate database configuration

        Returns:
            Dict dengan default estate paths
        """
        return {
            "PGE 1A": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/1a/PTRJ_P1A.FDB",
            "PGE 1B": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/1b/PTRJ_P1B.FDB",
            "PGE 2A": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/IFESS_PGE_2A/PTRJ_P2A.FDB",
            "PGE 2B": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/IFESS_2B/PTRJ_P2B.FDB",
            "IJL": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/IJL/PTRJ_IJL.FDB",
            "DME": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/dme/PTRJ_DME.FDB",
            "Are B2": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/Are B2/PTRJ_AB2.FDB",
            "Are B1": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/Are B1/PTRJ_AB1.FDB",
            "Are A": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/Are A/PTRJ_ARA.FDB",
            "Are C": "D:/Gawean Rebinmas/Monitoring Database/Database Ifess/Are C/PTRJ_ARC.FDB"
        }

    def _get_default_report_config(self) -> Dict:
        """
        Get default report configuration

        Returns:
            Dict dengan default report settings
        """
        return {
            "company": {
                "name": "PT. Rebinmas",
                "address": "Jakarta, Indonesia",
                "logo_path": "assets/company_logo.png"
            },
            "report": {
                "title": "FFB SCANNER DATA ANALYSIS REPORT",
                "subtitle": "Data Entry Quality Verification",
                "page_size": "A4",
                "margin": {
                    "top": 72,
                    "bottom": 72,
                    "left": 72,
                    "right": 72
                }
            },
            "tables": {
                "header_color": "#2E4053",
                "header_text_color": "white",
                "row_colors": ["#F8F9FA", "white"],
                "font_size": 9,
                "border_color": "#CCCCCC"
            },
            "charts": {
                "color_scheme": "#2E4053",
                "background_color": "#F8F9FA"
            },
            "output": {
                "default_format": "pdf",
                "output_directory": "reports",
                "filename_template": "FFB_Analysis_{estate}_{date_range}.pdf"
            }
        }

    def _get_default_analysis_config(self) -> Dict:
        """
        Get default analysis configuration

        Returns:
            Dict dengan analysis parameters
        """
        return {
            "verification": {
                "record_tags": {
                    "PM": "Kerani (Scanner)",
                    "P1": "Mandor (Supervisor)",
                    "P5": "Asisten (Assistant)"
                },
                "verification_rules": {
                    "require_pm": True,
                    "accept_p1_or_p5": True,
                    "both_p1_and_p5": False
                }
            },
            "performance": {
                "rating_thresholds": {
                    "excellent": 95,
                    "good": 85,
                    "fair": 70,
                    "poor": 50
                },
                "min_transactions_threshold": 10
            },
            "discrepancy": {
                "critical_fields": ["WEIGHT", "TREECOUNT", "BUNCHCOUNT"],
                "comparison_fields": ["AFD", "BLOCK", "TREECOUNT", "BUNCHCOUNT", "LOOSEFRUIT", "WEIGHT", "TBS", "HARVESTER", "TAKENBY"]
            },
            "data_quality": {
                "required_columns": ["TRANSNO", "SCANUSERID", "RECORDTAG", "TRANSDATE", "FIELDID"],
                "date_format": "%Y-%m-%d",
                "missing_value_threshold": 0.1  # 10%
            }
        }

    def _save_estate_config(self, config: Dict):
        """
        Save estate configuration ke file

        Args:
            config: Estate configuration dict
        """
        config_file = self.config_dir / "estate_config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            logger.info(f"Saved estate config to {config_file}")
        except Exception as e:
            logger.error(f"Error saving estate config: {e}")

    def _save_report_config(self, config: Dict):
        """
        Save report configuration ke file

        Args:
            config: Report configuration dict
        """
        config_file = self.config_dir / "report_config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            logger.info(f"Saved report config to {config_file}")
        except Exception as e:
            logger.error(f"Error saving report config: {e}")

    def get_estate_path(self, estate_name: str) -> Optional[str]:
        """
        Get database path untuk estate tertentu

        Args:
            estate_name: Nama estate

        Returns:
            Database path atau None jika tidak ditemukan
        """
        return self.estate_config.get(estate_name)

    def update_estate_path(self, estate_name: str, db_path: str):
        """
        Update database path untuk estate tertentu

        Args:
            estate_name: Nama estate
            db_path: Path ke database file
        """
        self.estate_config[estate_name] = db_path
        self._save_estate_config(self.estate_config)

    def get_all_estates(self) -> List[str]:
        """
        Get list semua estates yang terkonfigurasi

        Returns:
            List estate names
        """
        return list(self.estate_config.keys())

    def validate_estate_paths(self) -> Dict[str, bool]:
        """
        Validasi semua estate database paths

        Returns:
            Dict dengan estate name sebagai key dan validity sebagai value
        """
        results = {}
        for estate_name, db_path in self.estate_config.items():
            results[estate_name] = os.path.exists(db_path) if db_path else False

            if not results[estate_name]:
                logger.warning(f"Estate {estate_name} database path not found: {db_path}")

        return results

    def get_table_name_for_month(self, month: int) -> str:
        """
        Get table name untuk bulan tertentu

        Args:
            month: Month number (1-12)

        Returns:
            Table name (e.g., "FFBSCANNERDATA01")
        """
        return f"FFBSCANNERDATA{month:02d}"

    def get_month_list_from_range(self, start_date: str, end_date: str) -> List[int]:
        """
        Get list bulan dari date range

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List month numbers
        """
        from datetime import datetime
        from dateutil.relativedelta import relativedelta

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        months = []
        current = start
        while current <= end:
            months.append(current.month)
            current += relativedelta(months=1)

        return sorted(list(set(months)))  # Remove duplicates

    def get_output_path(self, filename: str = None) -> str:
        """
        Get output directory path untuk reports

        Args:
            filename: Optional filename

        Returns:
            Full path ke output file/directory
        """
        output_dir = Path(self.report_config["output"]["output_directory"])
        output_dir.mkdir(exist_ok=True)

        if filename:
            return str(output_dir / filename)
        else:
            return str(output_dir)

    def update_report_config(self, section: str, key: str, value):
        """
        Update report configuration value

        Args:
            section: Configuration section (e.g., "company", "report")
            key: Configuration key
            value: New value
        """
        if section in self.report_config:
            self.report_config[section][key] = value
            self._save_report_config(self.report_config)
            logger.info(f"Updated report config: {section}.{key} = {value}")

    def get_verification_rules(self) -> Dict:
        """
        Get verification rules

        Returns:
            Dict dengan verification rules
        """
        return self.analysis_config["verification"]

    def get_performance_thresholds(self) -> Dict:
        """
        Get performance rating thresholds

        Returns:
            Dict dengan rating thresholds
        """
        return self.analysis_config["performance"]["rating_thresholds"]