"""
Error display components for the Interview Prep Application UI.

Provides user-friendly error display, debugging information, and error recovery options.
"""

from datetime import datetime
from typing import Callable

import streamlit as st

from ..utils.error_handler import (
    ErrorRecord,
    ErrorCategory,
    ErrorSeverity,
    global_error_handler
)


class ErrorDisplayManager:
    """Manages error display in the Streamlit UI."""
    
    @staticmethod
    def show_error_message(
        error_record: ErrorRecord,
        show_details: bool = False,
        show_recovery_options: bool = True
    ) -> None:
        """
        Display a user-friendly error message.
        
        Args:
            error_record: The error record to display
            show_details: Whether to show technical details
            show_recovery_options: Whether to show recovery suggestions
        """
        # Determine error icon and color based on severity
        if error_record.severity == ErrorSeverity.CRITICAL:
            icon = "🚨"
            alert_type = "error"
        elif error_record.severity == ErrorSeverity.HIGH:
            icon = "❌"
            alert_type = "error"
        elif error_record.severity == ErrorSeverity.MEDIUM:
            icon = "⚠️"
            alert_type = "warning"
        else:
            icon = "ℹ️"
            alert_type = "info"
        
        # Display main error message
        if alert_type == "error":
            st.error(f"{icon} {error_record.user_message or error_record.error_message}")
        elif alert_type == "warning":
            st.warning(f"{icon} {error_record.user_message or error_record.error_message}")
        else:
            st.info(f"{icon} {error_record.user_message or error_record.error_message}")
        
        # Show recovery options
        if show_recovery_options:
            ErrorDisplayManager._show_recovery_options(error_record)
        
        # Show technical details if requested
        if show_details:
            ErrorDisplayManager._show_error_details(error_record)
    
    @staticmethod
    def _show_recovery_options(error_record: ErrorRecord) -> None:
        """Show recovery options based on error category."""
        suggestions = []
        
        if error_record.category == ErrorCategory.API_ERROR:
            suggestions = [
                "🔄 Check your internet connection",
                "🔑 Verify your API key is valid",
                "⏰ Try again in a moment",
                "💳 Check if you have API credits remaining"
            ]
        elif error_record.category == ErrorCategory.RATE_LIMIT_ERROR:
            suggestions = [
                "⏱️ Wait for the rate limit to reset",
                "🔄 Try again in a few minutes",
                "📊 Consider upgrading your API plan"
            ]
        elif error_record.category == ErrorCategory.VALIDATION_ERROR:
            suggestions = [
                "📝 Check your input for completeness",
                "📏 Verify text length requirements",
                "🛡️ Remove any special characters",
                "✏️ Rephrase your job description"
            ]
        elif error_record.category == ErrorCategory.NETWORK_ERROR:
            suggestions = [
                "🌐 Check your internet connection",
                "🔄 Refresh the page",
                "⏰ Try again in a moment"
            ]
        elif error_record.category == ErrorCategory.CONFIGURATION_ERROR:
            suggestions = [
                "🔑 Add your OpenAI API key",
                "⚙️ Check configuration settings",
                "📝 Review setup instructions"
            ]
        else:
            suggestions = [
                "🔄 Try refreshing the page",
                "⏰ Try again in a moment",
                "📞 Contact support if the issue persists"
            ]
        
        if suggestions:
            with st.expander("💡 Suggested Actions", expanded=False):
                for suggestion in suggestions:
                    st.write(f"• {suggestion}")
    
    @staticmethod
    def _show_error_details(error_record: ErrorRecord) -> None:
        """Show technical error details."""
        with st.expander("🔍 Technical Details", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Error Information:**")
                st.write(f"• **ID:** {error_record.error_id}")
                st.write(f"• **Type:** {error_record.error_type}")
                st.write(f"• **Category:** {error_record.category.value}")
                st.write(f"• **Severity:** {error_record.severity.value}")
                st.write(f"• **Time:** {error_record.timestamp.strftime('%H:%M:%S')}")
            
            with col2:
                st.write("**Operation Context:**")
                st.write(f"• **Operation:** {error_record.context.operation}")
                if error_record.context.additional_info:
                    for key, value in error_record.context.additional_info.items():
                        st.write(f"• **{key.title()}:** {value}")
            
            if error_record.recovery_attempted:
                st.write(f"**Recovery Attempted:** {'✅ Success' if error_record.recovery_successful else '❌ Failed'}")
            
            if error_record.stack_trace:
                st.text_area(
                    "Stack Trace",
                    value=error_record.stack_trace,
                    height=200,
                    help="Technical error details for debugging",
                    key=f"stack_trace_{error_record.error_id}"
                )
    
    @staticmethod
    def show_error_dashboard() -> None:
        """Display comprehensive error dashboard."""
        st.markdown("## 🚨 Error Dashboard")
        
        # Get error statistics
        stats = global_error_handler.get_error_statistics()
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Errors", stats["total_errors"])
        with col2:
            st.metric("Recent Errors (1h)", stats["recent_errors"])
        with col3:
            st.metric("Recovery Rate", f"{stats['recovery_success_rate']:.1f}%")
        with col4:
            last_error = stats["last_error"]
            if last_error:
                time_ago = datetime.now() - last_error.timestamp
                st.metric("Last Error", f"{time_ago.total_seconds():.0f}s ago")
            else:
                st.metric("Last Error", "None")
        
        # Error breakdown by category
        if stats["total_errors"] > 0:
            st.markdown("### Error Breakdown")
            
            error_data = []
            for category, count in stats["errors_by_category"].items():
                if count > 0:
                    error_data.append({
                        "Category": category.value.replace("_", " ").title(),
                        "Count": count,
                        "Percentage": f"{stats['error_rate_by_category'][category.value]:.1f}%"
                    })
            
            if error_data:
                st.table(error_data)
        
        # Most common errors
        if stats["most_common_errors"]:
            st.markdown("### Most Common Error Types")
            common_errors_data = []
            for error_type, count in stats["most_common_errors"]:
                common_errors_data.append({
                    "Error Type": error_type,
                    "Count": count
                })
            st.table(common_errors_data)
        
        # Recent errors
        recent_errors = global_error_handler.get_recent_errors(10)
        if recent_errors:
            st.markdown("### Recent Errors")
            
            for i, error in enumerate(reversed(recent_errors)):
                with st.expander(
                    f"#{len(recent_errors) - i} - {error.error_type} "
                    f"({error.timestamp.strftime('%H:%M:%S')})",
                    expanded=False
                ):
                    ErrorDisplayManager._show_error_details(error)
        
        # Error management actions
        st.markdown("### Error Management")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Clear Error History", help="Clear all stored error records"):
                global_error_handler.clear_error_history()
                st.success("Error history cleared!")
                st.rerun()
        
        with col2:
            if st.button("📊 Export Error Log", help="Export errors for analysis"):
                error_log = global_error_handler.export_error_log()
                if error_log:
                    st.download_button(
                        label="📥 Download Error Log",
                        data=str(error_log),
                        file_name=f"error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                else:
                    st.info("No errors to export")
        
        with col3:
            if st.button("🔄 Refresh Dashboard", help="Refresh error statistics"):
                st.rerun()
    
    @staticmethod
    def show_error_summary_widget() -> None:
        """Show a compact error summary widget for the sidebar."""
        stats = global_error_handler.get_error_statistics()
        
        if stats["total_errors"] > 0:
            st.markdown("### 🚨 Error Summary")
            
            # Recent errors indicator
            if stats["recent_errors"] > 0:
                st.error(f"⚠️ {stats['recent_errors']} error(s) in last hour")
            
            # Recovery rate
            recovery_rate = stats["recovery_success_rate"]
            if recovery_rate >= 80:
                st.success(f"✅ Recovery rate: {recovery_rate:.0f}%")
            elif recovery_rate >= 50:
                st.warning(f"⚠️ Recovery rate: {recovery_rate:.0f}%")
            else:
                st.error(f"❌ Recovery rate: {recovery_rate:.0f}%")
            
            # Quick stats
            st.caption(f"Total errors: {stats['total_errors']}")
            
            # Most common error
            if stats["most_common_errors"]:
                most_common = stats["most_common_errors"][0]
                st.caption(f"Most common: {most_common[0]} ({most_common[1]}x)")
        else:
            st.success("✅ No errors recorded")
    
    @staticmethod
    def handle_streamlit_error(error: Exception, context: str = "unknown") -> None:
        """
        Handle and display errors in Streamlit with proper logging.
        
        Args:
            error: The exception that occurred
            context: Context description for the error
        """
        from ..utils.error_handler import ErrorContext
        
        error_context = ErrorContext(
            operation=context,
            additional_info={"streamlit_context": True}
        )
        
        # Handle the error through the error handler
        recovery_successful, user_message, recovery_result = global_error_handler.handle_error(
            error, error_context, attempt_recovery=False
        )
        
        # Get the error record for display
        if global_error_handler.error_history:
            error_record = global_error_handler.error_history[-1]
            ErrorDisplayManager.show_error_message(
                error_record,
                show_details=st.session_state.get("debug_mode", False),
                show_recovery_options=True
            )
        else:
            # Fallback display
            st.error(f"An error occurred: {str(error)}")
    
    @staticmethod
    def create_error_recovery_button(
        error_record: ErrorRecord,
        recovery_action: Callable[[], bool],
        button_text: str = "🔄 Try Again"
    ) -> None:
        """
        Create a button for manual error recovery.
        
        Args:
            error_record: The error record associated with recovery
            recovery_action: Function to call for recovery
            button_text: Text for the recovery button
        """
        if st.button(button_text):
            try:
                with st.spinner("Attempting recovery..."):
                    result = recovery_action()
                    if result:
                        st.success("✅ Recovery successful!")
                        # Update error record
                        error_record.recovery_attempted = True
                        error_record.recovery_successful = True
                        st.rerun()
                    else:
                        st.error("❌ Recovery failed")
            except Exception as recovery_error:
                st.error(f"Recovery failed: {str(recovery_error)}")
                ErrorDisplayManager.handle_streamlit_error(
                    recovery_error, 
                    f"recovery_from_{error_record.error_id}"
                )


# Convenience functions for common error scenarios

def show_api_key_error() -> None:
    """Show API key configuration error."""
    st.error("🔑 API Key Required")
    st.info("""
    Please add your OpenAI API key to continue:
    
    1. Go to [OpenAI Platform](https://platform.openai.com)
    2. Navigate to API Keys section
    3. Create a new secret key
    4. Enter it in the configuration above
    """)


def show_network_error() -> None:
    """Show network connectivity error."""
    st.error("🌐 Network Connection Issue")
    st.info("""
    Please check your internet connection and try again.
    
    If the problem persists:
    - Verify your network connection
    - Check if OpenAI services are accessible
    - Try refreshing the page
    """)


def show_rate_limit_error(retry_after: int | None = None) -> None:
    """Show rate limit error with countdown."""
    if retry_after:
        st.warning(f"⏱️ Rate limit reached. Please wait {retry_after} seconds.")
        
        # Create a countdown if retry_after is reasonable (< 5 minutes)
        if retry_after <= 300:
            placeholder = st.empty()
            import time
            for remaining in range(retry_after, 0, -1):
                placeholder.info(f"⏱️ Rate limit reset in {remaining} seconds...")
                time.sleep(1)
            placeholder.success("✅ Rate limit reset! You can try again now.")
    else:
        st.warning("⏱️ Rate limit reached. Please wait a moment before trying again.")


def show_validation_error(field_name: str, message: str) -> None:
    """Show input validation error."""
    st.error(f"❌ Validation Error: {field_name}")
    st.info(f"Please fix the following issue: {message}")