"""
Employee Performance Service
Analyzes and calculates employee performance metrics
"""

from typing import Dict, Any, List, Optional, Tuple
from models.employee import Employee, EmployeeRole
from models.analysis_result import AnalysisResult, EmployeeMetrics


class EmployeePerformanceService:
    """
    Service for analyzing employee performance metrics
    """

    def calculate_employee_ranking(self, employees: List[Employee],
                                  metric: str = 'verification_rate',
                                  ascending: bool = False) -> List[Employee]:
        """
        Rank employees by specified metric

        :param employees: List of employees to rank
        :param metric: Metric to rank by
        :param ascending: Sort order (False for descending)
        :return: Ranked list of employees
        """
        def get_metric_value(employee: Employee) -> float:
            if metric == 'verification_rate':
                return employee.get_verification_rate()
            elif metric == 'difference_rate':
                return employee.get_difference_rate()
            elif metric == 'kerani_transactions':
                return employee.kerani_transactions
            elif metric == 'total_transactions':
                return employee.get_total_transactions()
            else:
                return 0.0

        # Filter to employees with transactions
        active_employees = [emp for emp in employees if emp.is_active()]

        # Sort by metric
        ranked_employees = sorted(
            active_employees,
            key=get_metric_value,
            reverse=not ascending
        )

        return ranked_employees

    def get_top_performers(self, employees: List[Employee],
                          limit: int = 10,
                          min_transactions: int = 5) -> List[Employee]:
        """
        Get top performing employees

        :param employees: List of employees
        :param limit: Maximum number to return
        :param min_transactions: Minimum transactions required
        :return: List of top performers
        """
        # Filter employees with minimum transactions
        qualified_employees = [
            emp for emp in employees
            if emp.kerani_transactions >= min_transactions
        ]

        # Rank by verification rate
        ranked = self.calculate_employee_ranking(
            qualified_employees, 'verification_rate'
        )

        return ranked[:limit]

    def get_problematic_employees(self, employees: List[Employee],
                                 min_differences: int = 1,
                                 min_transactions: int = 5) -> List[Employee]:
        """
        Get employees with quality issues

        :param employees: List of employees
        :param min_differences: Minimum differences required
        :param min_transactions: Minimum transactions required
        :return: List of problematic employees
        """
        problematic = []

        for employee in employees:
            if (employee.kerani_transactions >= min_transactions and
                employee.kerani_differences >= min_differences):
                problematic.append(employee)

        # Sort by difference rate (highest first)
        problematic.sort(key=lambda emp: emp.get_difference_rate(), reverse=True)

        return problematic

    def get_performance_distribution(self, employees: List[Employee]) -> Dict[str, Any]:
        """
        Get performance distribution statistics

        :param employees: List of employees
        :return: Performance distribution data
        """
        active_employees = [emp for emp in employees if emp.is_kerani()]

        if not active_employees:
            return {
                'total_employees': 0,
                'verification_ranges': {},
                'average_metrics': {}
            }

        verification_rates = [emp.get_verification_rate() for emp in active_employees]
        difference_rates = [emp.get_difference_rate() for emp in active_employees if emp.kerani_verified > 0]

        # Create verification rate ranges
        verification_ranges = {
            '0-25%': len([r for r in verification_rates if 0 <= r < 25]),
            '25-50%': len([r for r in verification_rates if 25 <= r < 50]),
            '50-75%': len([r for r in verification_rates if 50 <= r < 75]),
            '75-90%': len([r for r in verification_rates if 75 <= r < 90]),
            '90-100%': len([r for r in verification_rates if 90 <= r <= 100])
        }

        # Calculate averages
        average_metrics = {
            'verification_rate': sum(verification_rates) / len(verification_rates) if verification_rates else 0,
            'difference_rate': sum(difference_rates) / len(difference_rates) if difference_rates else 0,
            'transactions_per_employee': sum(emp.kerani_transactions for emp in active_employees) / len(active_employees)
        }

        return {
            'total_employees': len(active_employees),
            'verification_ranges': verification_ranges,
            'average_metrics': average_metrics,
            'min_verification_rate': min(verification_rates) if verification_rates else 0,
            'max_verification_rate': max(verification_rates) if verification_rates else 0,
            'median_verification_rate': sorted(verification_rates)[len(verification_rates)//2] if verification_rates else 0
        }

    def analyze_performance_trends(self, analysis_results: List[AnalysisResult],
                                  employee_id: str) -> Dict[str, Any]:
        """
        Analyze performance trends for an employee across multiple analysis results

        :param analysis_results: List of analysis results (chronological)
        :param employee_id: Employee ID to analyze
        :return: Trend analysis data
        """
        trends = {
            'employee_id': employee_id,
            'periods': [],
            'verification_rates': [],
            'difference_rates': [],
            'transaction_counts': []
        }

        for result in analysis_results:
            # Find employee in this result
            employee_metrics = None
            for division_summary in result.get_division_summaries():
                for emp_id, emp_metrics in division_summary.employee_details.items():
                    if emp_id == employee_id:
                        employee_metrics = emp_metrics
                        break
                if employee_metrics:
                    break

            if employee_metrics:
                period_str = f"{result.start_date.strftime('%d %b %Y')} - {result.end_date.strftime('%d %b %Y')}"
                trends['periods'].append(period_str)
                trends['verification_rates'].append(employee_metrics.verification_rate)
                trends['difference_rates'].append(employee_metrics.difference_rate)
                trends['transaction_counts'].append(employee_metrics.kerani_transactions)

        # Calculate trend indicators
        if len(trends['verification_rates']) >= 2:
            verification_trend = self._calculate_trend(trends['verification_rates'])
            difference_trend = self._calculate_trend(trends['difference_rates'])
            transaction_trend = self._calculate_trend(trends['transaction_counts'])

            trends['trends'] = {
                'verification_rate': verification_trend,
                'difference_rate': difference_trend,
                'transaction_count': transaction_trend
            }

        return trends

    def _calculate_trend(self, values: List[float]) -> Dict[str, Any]:
        """
        Calculate trend indicators for a series of values

        :param values: List of values
        :return: Trend analysis
        """
        if len(values) < 2:
            return {'direction': 'unknown', 'change': 0, 'percentage_change': 0}

        first_value = values[0]
        last_value = values[-1]
        change = last_value - first_value

        # Calculate percentage change
        percentage_change = 0
        if first_value != 0:
            percentage_change = (change / first_value) * 100

        # Determine trend direction
        if abs(change) < 0.01:  # Very small change
            direction = 'stable'
        elif change > 0:
            direction = 'improving'
        else:
            direction = 'declining'

        return {
            'direction': direction,
            'change': change,
            'percentage_change': percentage_change,
            'first_value': first_value,
            'last_value': last_value
        }

    def get_employee_comparison(self, employees: List[Employee],
                              employee_id: str) -> Dict[str, Any]:
        """
        Compare an employee against peer group

        :param employees: List of all employees
        :param employee_id: Employee to compare
        :return: Comparison analysis
        """
        target_employee = None
        for emp in employees:
            if emp.id == employee_id:
                target_employee = emp
                break

        if not target_employee:
            return {'error': f'Employee {employee_id} not found'}

        # Get peer group (same role, similar transaction volume)
        peer_group = [
            emp for emp in employees
            if (emp.id != employee_id and
                emp.is_kerani() and
                abs(emp.kerani_transactions - target_employee.kerani_transactions) <=
                max(10, target_employee.kerani_transactions * 0.2))  # Within 20% or 10 transactions
        ]

        if not peer_group:
            peer_group = [emp for emp in employees if emp.id != employee_id and emp.is_kerani()]

        if not peer_group:
            return {'error': 'No peer group found for comparison'}

        # Calculate percentiles
        verification_rates = [emp.get_verification_rate() for emp in peer_group]
        difference_rates = [emp.get_difference_rate() for emp in peer_group if emp.kerani_verified > 0]

        verification_percentile = self._calculate_percentile(
            target_employee.get_verification_rate(), verification_rates
        )

        difference_percentile = None
        if difference_rates and target_employee.kerani_verified > 0:
            difference_percentile = self._calculate_percentile(
                target_employee.get_difference_rate(), difference_rates
            )

        return {
            'employee': target_employee.to_dict(),
            'peer_group_size': len(peer_group),
            'verification_percentile': verification_percentile,
            'difference_percentile': difference_percentile,
            'peer_averages': {
                'verification_rate': sum(verification_rates) / len(verification_rates),
                'difference_rate': sum(difference_rates) / len(difference_rates) if difference_rates else 0,
                'transactions': sum(emp.kerani_transactions for emp in peer_group) / len(peer_group)
            },
            'ranking': {
                'verification_rank': self._get_rank(target_employee.get_verification_rate(), verification_rates),
                'total_peers': len(peer_group)
            }
        }

    def _calculate_percentile(self, value: float, data: List[float]) -> float:
        """
        Calculate percentile rank of a value in a dataset

        :param value: Value to calculate percentile for
        :param data: Dataset
        :return: Percentile (0-100)
        """
        if not data:
            return 0.0

        sorted_data = sorted(data)
        rank = sum(1 for x in sorted_data if x <= value)
        percentile = (rank / len(sorted_data)) * 100
        return percentile

    def _get_rank(self, value: float, data: List[float]) -> int:
        """
        Get rank of value in dataset (1-based)

        :param value: Value to rank
        :param data: Dataset
        :return: Rank (1-based, lower is better)
        """
        sorted_data = sorted(data, reverse=True)
        try:
            return sorted_data.index(value) + 1
        except ValueError:
            return len(sorted_data) + 1

    def generate_performance_recommendations(self, employee: Employee) -> List[str]:
        """
        Generate performance improvement recommendations

        :param employee: Employee to analyze
        :return: List of recommendations
        """
        recommendations = []

        verification_rate = employee.get_verification_rate()
        difference_rate = employee.get_difference_rate()

        # Low verification rate recommendations
        if verification_rate < 50:
            recommendations.append(
                f"Verification rate is very low ({verification_rate:.1f}%). "
                "Consider additional training on data entry procedures."
            )
        elif verification_rate < 75:
            recommendations.append(
                f"Verification rate could be improved ({verification_rate:.1f}%). "
                "Review transaction entry process for potential issues."
            )

        # High difference rate recommendations
        if difference_rate > 20:
            recommendations.append(
                f"High difference rate detected ({difference_rate:.1f}%). "
                "Attention to detail in data entry needs improvement."
            )
        elif difference_rate > 10:
            recommendations.append(
                f"Some data entry inconsistencies found ({difference_rate:.1f}%). "
                "Double-check field measurements before entry."
            )

        # Low transaction volume recommendations
        if employee.kerani_transactions < 50:
            recommendations.append(
                "Low transaction volume may indicate need for more practice "
                "or could reflect seasonal work patterns."
            )

        # Positive reinforcement
        if verification_rate > 90 and difference_rate < 5:
            recommendations.append(
                "Excellent performance! High verification rate with minimal differences."
            )

        if not recommendations:
            recommendations.append("Performance is within acceptable ranges.")

        return recommendations

    def create_performance_scorecard(self, employee: Employee,
                                   peer_group: List[Employee] = None) -> Dict[str, Any]:
        """
        Create comprehensive performance scorecard

        :param employee: Employee to scorecard
        :param peer_group: Optional peer group for comparison
        :return: Performance scorecard
        """
        scorecard = {
            'employee': employee.to_dict(),
            'metrics': {
                'verification_rate': employee.get_verification_rate(),
                'difference_rate': employee.get_difference_rate(),
                'total_transactions': employee.get_total_transactions(),
                'kerani_transactions': employee.kerani_transactions
            },
            'scores': {},
            'recommendations': self.generate_performance_recommendations(employee)
        }

        # Calculate performance scores
        scorecard['scores']['verification_score'] = min(100, employee.get_verification_rate())
        scorecard['scores']['quality_score'] = max(0, 100 - employee.get_difference_rate())
        scorecard['scores']['volume_score'] = min(100, (employee.kerani_transactions / 100) * 100)

        # Overall score (weighted average)
        scorecard['scores']['overall_score'] = (
            scorecard['scores']['verification_score'] * 0.5 +
            scorecard['scores']['quality_score'] * 0.3 +
            scorecard['scores']['volume_score'] * 0.2
        )

        # Add peer comparison if available
        if peer_group:
            comparison = self.get_employee_comparison(peer_group, employee.id)
            scorecard['peer_comparison'] = comparison

        # Performance grade
        overall_score = scorecard['scores']['overall_score']
        if overall_score >= 90:
            scorecard['grade'] = 'A'
        elif overall_score >= 80:
            scorecard['grade'] = 'B'
        elif overall_score >= 70:
            scorecard['grade'] = 'C'
        elif overall_score >= 60:
            scorecard['grade'] = 'D'
        else:
            scorecard['grade'] = 'F'

        return scorecard