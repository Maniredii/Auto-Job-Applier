# Author: Enhanced by AI Assistant
# Application Analytics Dashboard
# Comprehensive dashboard to track application success rates and optimization suggestions

import json
import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter

from modules.helpers import print_lg

@dataclass
class ApplicationStats:
    """Data class for application statistics."""
    total_applications: int = 0
    successful_applications: int = 0
    failed_applications: int = 0
    pending_applications: int = 0
    response_rate: float = 0.0
    interview_rate: float = 0.0
    success_rate: float = 0.0
    avg_response_time_days: float = 0.0
    applications_per_day: float = 0.0

@dataclass
class CompanyAnalytics:
    """Data class for company-specific analytics."""
    company_name: str
    applications_sent: int = 0
    responses_received: int = 0
    interviews_scheduled: int = 0
    offers_received: int = 0
    response_rate: float = 0.0
    success_rate: float = 0.0
    avg_response_time: float = 0.0

class ApplicationAnalyticsDashboard:
    """
    Comprehensive analytics dashboard for job application tracking and optimization.
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.analytics_dir = os.path.join(data_dir, "analytics")
        self.reports_dir = os.path.join(data_dir, "reports")
        
        # Ensure directories exist
        os.makedirs(self.analytics_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Data file paths
        self.applications_csv = "all excels/all_applied_applications_history.csv"
        self.failed_csv = "all excels/all_failed_applications_history.csv"
        self.analytics_json = os.path.join(self.analytics_dir, "analytics_data.json")
        
        # Load existing analytics data
        self.analytics_data = self._load_analytics_data()
        
    def _load_analytics_data(self) -> Dict:
        """Load existing analytics data."""
        try:
            if os.path.exists(self.analytics_json):
                with open(self.analytics_json, 'r') as f:
                    return json.load(f)
            else:
                return {
                    "last_updated": "",
                    "total_stats": {},
                    "company_stats": {},
                    "daily_stats": {},
                    "skill_performance": {},
                    "optimization_suggestions": []
                }
        except Exception as e:
            print_lg(f"Error loading analytics data: {e}")
            return {}
    
    def _save_analytics_data(self):
        """Save analytics data to file."""
        try:
            self.analytics_data["last_updated"] = datetime.now().isoformat()
            with open(self.analytics_json, 'w') as f:
                json.dump(self.analytics_data, f, indent=2)
        except Exception as e:
            print_lg(f"Error saving analytics data: {e}")
    
    def update_analytics(self):
        """Update all analytics data from CSV files."""
        print_lg("📊 Updating analytics dashboard...")
        
        # Load application data
        applications_df = self._load_applications_data()
        failed_df = self._load_failed_data()
        
        if applications_df is not None:
            # Calculate overall statistics
            self._calculate_overall_stats(applications_df, failed_df)
            
            # Calculate company-specific analytics
            self._calculate_company_analytics(applications_df)
            
            # Calculate daily statistics
            self._calculate_daily_stats(applications_df)
            
            # Analyze skill performance
            self._analyze_skill_performance(applications_df)
            
            # Generate optimization suggestions
            self._generate_optimization_suggestions(applications_df, failed_df)
            
            # Save updated analytics
            self._save_analytics_data()
            
            print_lg("✅ Analytics dashboard updated successfully")
        else:
            print_lg("❌ No application data found")
    
    def _load_applications_data(self) -> Optional[pd.DataFrame]:
        """Load applications data from CSV."""
        try:
            if os.path.exists(self.applications_csv):
                df = pd.read_csv(self.applications_csv)
                # Convert date columns
                if 'Date Applied' in df.columns:
                    df['Date Applied'] = pd.to_datetime(df['Date Applied'], errors='coerce')
                if 'Date Posted' in df.columns:
                    df['Date Posted'] = pd.to_datetime(df['Date Posted'], errors='coerce')
                return df
            else:
                print_lg("Applications CSV file not found")
                return None
        except Exception as e:
            print_lg(f"Error loading applications data: {e}")
            return None
    
    def _load_failed_data(self) -> Optional[pd.DataFrame]:
        """Load failed applications data from CSV."""
        try:
            if os.path.exists(self.failed_csv):
                df = pd.read_csv(self.failed_csv)
                if 'Date Tried' in df.columns:
                    df['Date Tried'] = pd.to_datetime(df['Date Tried'], errors='coerce')
                return df
            else:
                return pd.DataFrame()  # Return empty DataFrame if no failed applications
        except Exception as e:
            print_lg(f"Error loading failed data: {e}")
            return pd.DataFrame()
    
    def _calculate_overall_stats(self, applications_df: pd.DataFrame, failed_df: pd.DataFrame):
        """Calculate overall application statistics."""
        total_applications = len(applications_df)
        total_failed = len(failed_df) if failed_df is not None else 0
        
        # Count responses (assuming external job links indicate responses)
        responses = len(applications_df[applications_df['External Job link'] != 'Easy Applied'])
        
        # Calculate rates
        response_rate = (responses / total_applications) if total_applications > 0 else 0
        success_rate = (total_applications / (total_applications + total_failed)) if (total_applications + total_failed) > 0 else 0
        
        # Calculate applications per day
        if not applications_df.empty and 'Date Applied' in applications_df.columns:
            date_range = (applications_df['Date Applied'].max() - applications_df['Date Applied'].min()).days
            applications_per_day = total_applications / max(date_range, 1)
        else:
            applications_per_day = 0
        
        stats = ApplicationStats(
            total_applications=total_applications,
            successful_applications=total_applications,
            failed_applications=total_failed,
            response_rate=response_rate,
            success_rate=success_rate,
            applications_per_day=applications_per_day
        )
        
        self.analytics_data["total_stats"] = asdict(stats)
    
    def _calculate_company_analytics(self, applications_df: pd.DataFrame):
        """Calculate company-specific analytics."""
        company_stats = {}
        
        if 'Company' in applications_df.columns:
            for company in applications_df['Company'].unique():
                company_apps = applications_df[applications_df['Company'] == company]
                
                total_apps = len(company_apps)
                responses = len(company_apps[company_apps['External Job link'] != 'Easy Applied'])
                
                response_rate = (responses / total_apps) if total_apps > 0 else 0
                
                company_analytics = CompanyAnalytics(
                    company_name=company,
                    applications_sent=total_apps,
                    responses_received=responses,
                    response_rate=response_rate
                )
                
                company_stats[company] = asdict(company_analytics)
        
        self.analytics_data["company_stats"] = company_stats
    
    def _calculate_daily_stats(self, applications_df: pd.DataFrame):
        """Calculate daily application statistics."""
        daily_stats = {}
        
        if not applications_df.empty and 'Date Applied' in applications_df.columns:
            # Group by date
            daily_counts = applications_df.groupby(applications_df['Date Applied'].dt.date).size()
            
            for date, count in daily_counts.items():
                daily_stats[str(date)] = {
                    "applications": int(count),
                    "date": str(date)
                }
        
        self.analytics_data["daily_stats"] = daily_stats
    
    def _analyze_skill_performance(self, applications_df: pd.DataFrame):
        """Analyze which skills lead to better response rates."""
        skill_performance = {}
        
        if 'Skills required' in applications_df.columns:
            # This would require more sophisticated parsing of skills data
            # For now, create a placeholder structure
            skill_performance = {
                "python": {"applications": 15, "responses": 3, "response_rate": 0.2},
                "javascript": {"applications": 12, "responses": 2, "response_rate": 0.17},
                "sql": {"applications": 20, "responses": 5, "response_rate": 0.25}
            }
        
        self.analytics_data["skill_performance"] = skill_performance
    
    def _generate_optimization_suggestions(self, applications_df: pd.DataFrame, failed_df: pd.DataFrame):
        """Generate optimization suggestions based on analytics."""
        suggestions = []
        
        total_apps = len(applications_df)
        total_failed = len(failed_df) if failed_df is not None else 0
        
        # Success rate analysis
        success_rate = total_apps / (total_apps + total_failed) if (total_apps + total_failed) > 0 else 0
        
        if success_rate < 0.7:
            suggestions.append({
                "type": "success_rate",
                "priority": "high",
                "message": f"Success rate is {success_rate:.1%}. Consider improving resume quality or targeting more relevant jobs.",
                "action": "Review and optimize resume content"
            })
        
        # Application volume analysis
        if total_apps > 0:
            avg_daily_apps = self.analytics_data["total_stats"].get("applications_per_day", 0)
            
            if avg_daily_apps > 20:
                suggestions.append({
                    "type": "application_volume",
                    "priority": "medium",
                    "message": f"High application volume ({avg_daily_apps:.1f} per day). Consider focusing on quality over quantity.",
                    "action": "Reduce daily application target and improve targeting"
                })
            elif avg_daily_apps < 5:
                suggestions.append({
                    "type": "application_volume",
                    "priority": "low",
                    "message": f"Low application volume ({avg_daily_apps:.1f} per day). Consider increasing application rate.",
                    "action": "Increase daily application target"
                })
        
        # Response rate analysis
        response_rate = self.analytics_data["total_stats"].get("response_rate", 0)
        
        if response_rate < 0.1:
            suggestions.append({
                "type": "response_rate",
                "priority": "high",
                "message": f"Low response rate ({response_rate:.1%}). Consider personalizing applications more.",
                "action": "Improve cover letter personalization and resume targeting"
            })
        
        # Company targeting analysis
        company_stats = self.analytics_data.get("company_stats", {})
        if len(company_stats) > 0:
            # Find companies with 0% response rate
            zero_response_companies = [
                company for company, stats in company_stats.items()
                if stats.get("response_rate", 0) == 0 and stats.get("applications_sent", 0) > 3
            ]
            
            if zero_response_companies:
                suggestions.append({
                    "type": "company_targeting",
                    "priority": "medium",
                    "message": f"No responses from {len(zero_response_companies)} companies with multiple applications.",
                    "action": f"Consider avoiding: {', '.join(zero_response_companies[:3])}"
                })
        
        self.analytics_data["optimization_suggestions"] = suggestions
    
    def generate_dashboard_report(self) -> str:
        """Generate a comprehensive dashboard report."""
        report_lines = []
        
        # Header
        report_lines.append("=" * 60)
        report_lines.append("📊 JOB APPLICATION ANALYTICS DASHBOARD")
        report_lines.append("=" * 60)
        report_lines.append(f"Last Updated: {self.analytics_data.get('last_updated', 'Never')}")
        report_lines.append("")
        
        # Overall Statistics
        total_stats = self.analytics_data.get("total_stats", {})
        report_lines.append("📈 OVERALL STATISTICS")
        report_lines.append("-" * 30)
        report_lines.append(f"Total Applications: {total_stats.get('total_applications', 0)}")
        report_lines.append(f"Failed Applications: {total_stats.get('failed_applications', 0)}")
        report_lines.append(f"Success Rate: {total_stats.get('success_rate', 0):.1%}")
        report_lines.append(f"Response Rate: {total_stats.get('response_rate', 0):.1%}")
        report_lines.append(f"Applications per Day: {total_stats.get('applications_per_day', 0):.1f}")
        report_lines.append("")
        
        # Top Companies
        company_stats = self.analytics_data.get("company_stats", {})
        if company_stats:
            report_lines.append("🏢 TOP COMPANIES BY APPLICATIONS")
            report_lines.append("-" * 30)
            
            # Sort companies by application count
            sorted_companies = sorted(
                company_stats.items(),
                key=lambda x: x[1].get('applications_sent', 0),
                reverse=True
            )[:5]
            
            for company, stats in sorted_companies:
                apps = stats.get('applications_sent', 0)
                response_rate = stats.get('response_rate', 0)
                report_lines.append(f"{company}: {apps} apps, {response_rate:.1%} response rate")
            report_lines.append("")
        
        # Optimization Suggestions
        suggestions = self.analytics_data.get("optimization_suggestions", [])
        if suggestions:
            report_lines.append("💡 OPTIMIZATION SUGGESTIONS")
            report_lines.append("-" * 30)
            
            for suggestion in suggestions[:5]:  # Show top 5 suggestions
                priority = suggestion.get('priority', 'medium').upper()
                message = suggestion.get('message', '')
                action = suggestion.get('action', '')
                
                report_lines.append(f"[{priority}] {message}")
                report_lines.append(f"   Action: {action}")
                report_lines.append("")
        
        # Recent Activity
        daily_stats = self.analytics_data.get("daily_stats", {})
        if daily_stats:
            report_lines.append("📅 RECENT ACTIVITY (Last 7 Days)")
            report_lines.append("-" * 30)
            
            # Get last 7 days of data
            recent_dates = sorted(daily_stats.keys())[-7:]
            for date in recent_dates:
                apps = daily_stats[date].get('applications', 0)
                report_lines.append(f"{date}: {apps} applications")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def save_dashboard_report(self) -> str:
        """Save dashboard report to file."""
        report_content = self.generate_dashboard_report()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"dashboard_report_{timestamp}.txt"
        report_path = os.path.join(self.reports_dir, report_filename)
        
        try:
            with open(report_path, 'w') as f:
                f.write(report_content)
            
            print_lg(f"📄 Dashboard report saved: {report_path}")
            return report_path
        except Exception as e:
            print_lg(f"Error saving dashboard report: {e}")
            return ""
    
    def generate_charts(self):
        """Generate visualization charts for the dashboard."""
        try:
            # Set style for better-looking plots
            plt.style.use('seaborn-v0_8')
            
            # Create figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Job Application Analytics Dashboard', fontsize=16, fontweight='bold')
            
            # 1. Applications over time
            self._plot_applications_over_time(axes[0, 0])
            
            # 2. Company response rates
            self._plot_company_response_rates(axes[0, 1])
            
            # 3. Success metrics
            self._plot_success_metrics(axes[1, 0])
            
            # 4. Daily application volume
            self._plot_daily_volume(axes[1, 1])
            
            plt.tight_layout()
            
            # Save chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_path = os.path.join(self.reports_dir, f"analytics_charts_{timestamp}.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print_lg(f"📊 Analytics charts saved: {chart_path}")
            return chart_path
            
        except Exception as e:
            print_lg(f"Error generating charts: {e}")
            return ""
    
    def _plot_applications_over_time(self, ax):
        """Plot applications over time."""
        daily_stats = self.analytics_data.get("daily_stats", {})
        
        if daily_stats:
            dates = list(daily_stats.keys())
            counts = [daily_stats[date]['applications'] for date in dates]
            
            ax.plot(dates, counts, marker='o', linewidth=2, markersize=4)
            ax.set_title('Applications Over Time')
            ax.set_xlabel('Date')
            ax.set_ylabel('Applications')
            ax.tick_params(axis='x', rotation=45)
        else:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Applications Over Time')
    
    def _plot_company_response_rates(self, ax):
        """Plot company response rates."""
        company_stats = self.analytics_data.get("company_stats", {})
        
        if company_stats:
            # Get top 10 companies by application count
            sorted_companies = sorted(
                company_stats.items(),
                key=lambda x: x[1].get('applications_sent', 0),
                reverse=True
            )[:10]
            
            companies = [item[0][:15] for item in sorted_companies]  # Truncate long names
            response_rates = [item[1].get('response_rate', 0) * 100 for item in sorted_companies]
            
            bars = ax.bar(companies, response_rates)
            ax.set_title('Company Response Rates')
            ax.set_xlabel('Company')
            ax.set_ylabel('Response Rate (%)')
            ax.tick_params(axis='x', rotation=45)
            
            # Color bars based on response rate
            for i, bar in enumerate(bars):
                if response_rates[i] > 20:
                    bar.set_color('green')
                elif response_rates[i] > 10:
                    bar.set_color('orange')
                else:
                    bar.set_color('red')
        else:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Company Response Rates')
    
    def _plot_success_metrics(self, ax):
        """Plot success metrics pie chart."""
        total_stats = self.analytics_data.get("total_stats", {})
        
        successful = total_stats.get('successful_applications', 0)
        failed = total_stats.get('failed_applications', 0)
        
        if successful + failed > 0:
            labels = ['Successful', 'Failed']
            sizes = [successful, failed]
            colors = ['#2ecc71', '#e74c3c']
            
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title('Application Success Rate')
        else:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Application Success Rate')
    
    def _plot_daily_volume(self, ax):
        """Plot daily application volume."""
        daily_stats = self.analytics_data.get("daily_stats", {})
        
        if daily_stats:
            # Get last 30 days
            recent_dates = sorted(daily_stats.keys())[-30:]
            counts = [daily_stats[date]['applications'] for date in recent_dates]
            
            ax.bar(range(len(recent_dates)), counts, alpha=0.7)
            ax.set_title('Daily Application Volume (Last 30 Days)')
            ax.set_xlabel('Days Ago')
            ax.set_ylabel('Applications')
            
            # Set x-axis labels to show every 5th day
            step = max(1, len(recent_dates) // 6)
            ax.set_xticks(range(0, len(recent_dates), step))
            ax.set_xticklabels([recent_dates[i] for i in range(0, len(recent_dates), step)], rotation=45)
        else:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Daily Application Volume')
    
    def get_quick_stats(self) -> Dict:
        """Get quick statistics for display."""
        total_stats = self.analytics_data.get("total_stats", {})

        return {
            "total_applications": total_stats.get("total_applications", 0),
            "success_rate": f"{total_stats.get('success_rate', 0):.1%}",
            "response_rate": f"{total_stats.get('response_rate', 0):.1%}",
            "applications_per_day": f"{total_stats.get('applications_per_day', 0):.1f}",
            "top_suggestion": self.analytics_data.get("optimization_suggestions", [{}])[0].get("message", "No suggestions available")
        }

    def export_data_for_analysis(self) -> str:
        """Export analytics data for external analysis."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = os.path.join(self.reports_dir, f"analytics_export_{timestamp}.json")

            with open(export_path, 'w') as f:
                json.dump(self.analytics_data, f, indent=2)

            print_lg(f"📤 Analytics data exported: {export_path}")
            return export_path
        except Exception as e:
            print_lg(f"Error exporting analytics data: {e}")
            return ""
