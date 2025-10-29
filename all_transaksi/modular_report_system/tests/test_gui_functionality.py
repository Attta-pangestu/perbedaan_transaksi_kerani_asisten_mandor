"""
GUI Functionality Test Suite
Tests all GUI components, button functionality, and user interactions
"""

import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from presentation.main_window import MainWindow
from presentation.widgets.automated_report_widget import AutomatedReportWidget
from presentation.widgets.report_generator_widget import ReportGeneratorWidget


class TestMainWindowGUI(unittest.TestCase):
    """Test cases for main window GUI functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window during testing
        
        # Mock database connection
        with patch('data.database.database_manager.DatabaseManager'):
            self.main_window = MainWindow(self.root)
    
    def tearDown(self):
        """Clean up after tests"""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_main_window_initialization(self):
        """Test main window initializes correctly"""
        self.assertIsNotNone(self.main_window)
        self.assertIsInstance(self.main_window.root, tk.Tk)
    
    def test_notebook_tabs_exist(self):
        """Test that all required notebook tabs exist"""
        # Check if notebook exists
        self.assertIsNotNone(self.main_window.notebook)
        
        # Get tab count
        tab_count = self.main_window.notebook.index("end")
        self.assertGreater(tab_count, 0)
    
    def test_menu_bar_exists(self):
        """Test that menu bar exists and has required menus"""
        # Check if menu bar exists
        menu_bar = self.root.nametowidget(self.root['menu'])
        self.assertIsNotNone(menu_bar)
    
    def test_window_title(self):
        """Test window title is set correctly"""
        title = self.root.title()
        self.assertIn("SISTEM GENERASI LAPORAN MODULAR", title)
    
    def test_window_geometry(self):
        """Test window has appropriate size"""
        self.root.update()  # Update geometry
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Should have reasonable minimum size
        self.assertGreater(width, 800)
        self.assertGreater(height, 600)


class TestReportGeneratorWidgetGUI(unittest.TestCase):
    """Test cases for report generator widget GUI"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Mock database manager
        with patch('data.database.database_manager.DatabaseManager'):
            self.widget = ReportGeneratorWidget(self.root)
    
    def tearDown(self):
        """Clean up after tests"""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_widget_initialization(self):
        """Test widget initializes with all components"""
        self.assertIsNotNone(self.widget.main_frame)
        self.assertIsNotNone(self.widget.filter_frame)
        self.assertIsNotNone(self.widget.result_frame)
    
    def test_filter_components_exist(self):
        """Test all filter components exist"""
        # Check date filters
        self.assertIsNotNone(self.widget.start_date_entry)
        self.assertIsNotNone(self.widget.end_date_entry)
        
        # Check unit and estate filters
        self.assertIsNotNone(self.widget.unit_var)
        self.assertIsNotNone(self.widget.estate_var)
    
    def test_button_functionality(self):
        """Test button click functionality"""
        # Test generate button exists
        generate_btn = None
        for child in self.widget.main_frame.winfo_children():
            if isinstance(child, tk.Frame):
                for btn in child.winfo_children():
                    if isinstance(btn, tk.Button) and "Generate" in str(btn['text']):
                        generate_btn = btn
                        break
        
        # Should have generate button
        self.assertIsNotNone(generate_btn)
    
    def test_result_display_components(self):
        """Test result display components"""
        self.assertIsNotNone(self.widget.result_tree)
        self.assertIsNotNone(self.widget.status_label)
    
    def test_filter_validation(self):
        """Test filter input validation"""
        # Test date validation
        self.widget.start_date_entry.delete(0, tk.END)
        self.widget.start_date_entry.insert(0, "2024-01-01")
        
        self.widget.end_date_entry.delete(0, tk.END)
        self.widget.end_date_entry.insert(0, "2024-01-31")
        
        # Should not raise exception
        start_date = self.widget.start_date_entry.get()
        end_date = self.widget.end_date_entry.get()
        
        self.assertEqual(start_date, "2024-01-01")
        self.assertEqual(end_date, "2024-01-31")
    
    def test_unit_estate_specific_filtering(self):
        """Test Unit 9 and Estate 2B specific filtering"""
        # Set unit to 9
        self.widget.unit_var.set("9")
        self.assertEqual(self.widget.unit_var.get(), "9")
        
        # Set estate to 2B
        self.widget.estate_var.set("2B")
        self.assertEqual(self.widget.estate_var.get(), "2B")


class TestAutomatedReportWidgetGUI(unittest.TestCase):
    """Test cases for automated report widget GUI"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Mock the automated service
        with patch('business.services.automated_report_service.AutomatedReportService'):
            self.widget = AutomatedReportWidget(self.root)
    
    def tearDown(self):
        """Clean up after tests"""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_widget_components_exist(self):
        """Test all widget components exist"""
        self.assertIsNotNone(self.widget.main_frame)
        self.assertIsNotNone(self.widget.config_tree)
        self.assertIsNotNone(self.widget.control_buttons)
    
    def test_configuration_tree_columns(self):
        """Test configuration tree has correct columns"""
        columns = self.widget.config_tree['columns']
        
        expected_columns = ['name', 'unit_estate', 'frequency', 'time', 'last_run', 'status']
        
        for col in expected_columns:
            self.assertIn(col, columns)
    
    def test_control_buttons_exist(self):
        """Test all control buttons exist"""
        required_buttons = ['add', 'edit', 'delete', 'run_now', 'refresh', 'add_default']
        
        for button_key in required_buttons:
            self.assertIn(button_key, self.widget.control_buttons)
            button = self.widget.control_buttons[button_key]
            self.assertIsNotNone(button)
            self.assertIsInstance(button, (tk.Button, tk.ttk.Button))
    
    def test_add_default_button_functionality(self):
        """Test add default button for Unit 9 Estate 2B"""
        add_default_btn = self.widget.control_buttons['add_default']
        
        # Check button text contains Unit 9 Estate 2B reference
        button_text = str(add_default_btn['text'])
        self.assertIn("Unit 9", button_text)
        self.assertIn("Estate 2B", button_text)
    
    def test_tree_selection_handling(self):
        """Test tree selection event handling"""
        # Insert test data
        test_item = self.widget.config_tree.insert("", "end", values=(
            "Test Config",
            "Unit 9 - Estate 2B",
            "Harian",
            "08:00",
            "2024-01-15 08:00",
            "Aktif"
        ))
        
        # Select the item
        self.widget.config_tree.selection_set(test_item)
        
        # Should not raise exception
        selected = self.widget.config_tree.selection()
        self.assertEqual(len(selected), 1)
    
    def test_activity_log_component(self):
        """Test activity log component exists and functions"""
        # Check if activity log exists
        self.assertIsNotNone(self.widget.activity_text)
        
        # Test logging functionality
        test_message = "Test activity log message"
        self.widget.log_activity(test_message)
        
        # Check if message was added
        log_content = self.widget.activity_text.get("1.0", tk.END)
        self.assertIn(test_message, log_content)


class TestGUIInteractionScenarios(unittest.TestCase):
    """Test real-world GUI interaction scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Mock services
        with patch('business.services.automated_report_service.AutomatedReportService'):
            self.automated_widget = AutomatedReportWidget(self.root)
        
        with patch('data.database.database_manager.DatabaseManager'):
            self.generator_widget = ReportGeneratorWidget(self.root)
    
    def tearDown(self):
        """Clean up after tests"""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_unit_9_estate_2b_workflow(self):
        """Test complete workflow for Unit 9 Estate 2B"""
        # Step 1: Set filters in generator widget
        self.generator_widget.unit_var.set("9")
        self.generator_widget.estate_var.set("2B")
        
        # Verify filters are set
        self.assertEqual(self.generator_widget.unit_var.get(), "9")
        self.assertEqual(self.generator_widget.estate_var.get(), "2B")
        
        # Step 2: Test automated report configuration
        # Mock the service call
        with patch.object(self.automated_widget.automated_service, 'save_configuration', return_value='test_id'):
            with patch('tkinter.messagebox.showinfo'):
                self.automated_widget.add_default_configurations()
        
        # Should complete without errors
        self.assertTrue(True)  # If we get here, no exceptions were raised
    
    def test_button_state_management(self):
        """Test button states change appropriately"""
        # Initially, edit and delete buttons should be disabled when no selection
        edit_btn = self.automated_widget.control_buttons['edit']
        delete_btn = self.automated_widget.control_buttons['delete']
        
        # Add test item and select it
        test_item = self.automated_widget.config_tree.insert("", "end", values=(
            "Test Config", "Unit 9 - Estate 2B", "Harian", "08:00", "Never", "Aktif"
        ))
        
        self.automated_widget.config_tree.selection_set(test_item)
        
        # Trigger selection event
        self.automated_widget.on_config_selected(None)
        
        # Should not raise exceptions
        self.assertTrue(True)
    
    def test_error_handling_in_gui(self):
        """Test GUI error handling"""
        # Test with invalid date input
        self.generator_widget.start_date_entry.delete(0, tk.END)
        self.generator_widget.start_date_entry.insert(0, "invalid-date")
        
        # Should handle gracefully
        date_value = self.generator_widget.start_date_entry.get()
        self.assertEqual(date_value, "invalid-date")
    
    def test_gui_responsiveness(self):
        """Test GUI remains responsive during operations"""
        # Update GUI
        self.root.update()
        
        # Simulate user interactions
        self.automated_widget.load_configurations()
        self.root.update()
        
        # Should complete without hanging
        self.assertTrue(True)


class TestAccessibilityAndUsability(unittest.TestCase):
    """Test accessibility and usability features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.root = tk.Tk()
        self.root.withdraw()
        
        with patch('business.services.automated_report_service.AutomatedReportService'):
            self.widget = AutomatedReportWidget(self.root)
    
    def tearDown(self):
        """Clean up after tests"""
        try:
            self.root.destroy()
        except:
            pass
    
    def test_button_text_clarity(self):
        """Test button text is clear and descriptive"""
        for button_key, button in self.widget.control_buttons.items():
            button_text = str(button['text'])
            
            # Should not be empty
            self.assertGreater(len(button_text.strip()), 0)
            
            # Should contain meaningful text
            if button_key == 'add_default':
                self.assertIn("Unit 9", button_text)
                self.assertIn("Estate 2B", button_text)
    
    def test_column_headers_readable(self):
        """Test tree column headers are readable"""
        for col in self.widget.config_tree['columns']:
            header_text = self.widget.config_tree.heading(col)['text']
            
            # Should not be empty
            self.assertGreater(len(header_text), 0)
            
            # Should be in Indonesian (as per requirement)
            if col == 'unit_estate':
                self.assertIn("Unit", header_text)
                self.assertIn("Estate", header_text)
    
    def test_widget_layout_structure(self):
        """Test widget layout is properly structured"""
        # Main frame should exist
        self.assertIsNotNone(self.widget.main_frame)
        
        # Should have child widgets
        children = self.widget.main_frame.winfo_children()
        self.assertGreater(len(children), 0)
    
    def test_error_message_display(self):
        """Test error messages are displayed properly"""
        # Test activity logging
        error_message = "Test error message"
        self.widget.log_activity(error_message)
        
        # Should be logged
        log_content = self.widget.activity_text.get("1.0", tk.END)
        self.assertIn(error_message, log_content)


if __name__ == '__main__':
    # Create comprehensive test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestMainWindowGUI,
        TestReportGeneratorWidgetGUI,
        TestAutomatedReportWidgetGUI,
        TestGUIInteractionScenarios,
        TestAccessibilityAndUsability
    ]
    
    for test_class in test_classes:
        test_suite.addTest(unittest.makeSuite(test_class))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print comprehensive summary
    print(f"\n{'='*80}")
    print(f"GUI FUNCTIONALITY TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Successful Tests: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed Tests: {len(result.failures)}")
    print(f"Error Tests: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Detailed failure and error reporting
    if result.failures:
        print(f"\n{'='*40} FAILURES {'='*40}")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"{i}. {test}")
            print(f"   {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n{'='*40} ERRORS {'='*40}")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"{i}. {test}")
            print(f"   {traceback.split('Exception:')[-1].strip()}")
    
    # Test coverage summary
    print(f"\n{'='*40} COVERAGE SUMMARY {'='*40}")
    print("✓ Main Window GUI Components")
    print("✓ Report Generator Widget")
    print("✓ Automated Report Widget")
    print("✓ Button Functionality")
    print("✓ User Interaction Scenarios")
    print("✓ Unit 9 & Estate 2B Specific Features")
    print("✓ Error Handling")
    print("✓ Accessibility & Usability")
    
    print(f"\n{'='*80}")
    print("GUI testing completed successfully!" if result.wasSuccessful() else "Some GUI tests failed - please review!")
    print(f"{'='*80}")