"""
Settings page - AI Provider Configuration.

Allows users to configure and switch between AI providers:
- Local AI: Ollama (llama3, mistral, gemma3)
- Cloud AI: OpenAI, Gemini, OpenRouter (BYOK)

API keys are stored only in Streamlit session state, never persisted to disk.
"""

import streamlit as st
import logging
from services.ai_service import AIService
from database.repository import SettingsRepository

logger = logging.getLogger(__name__)


def render_settings():
    """Render the AI provider settings page."""
    st.title("⚙️ Settings")
    st.markdown("Configure your AI provider preferences")
    st.divider()

    # AI Provider Configuration Section
    st.header("🤖 AI Provider Configuration")
    st.markdown("Choose between **Local AI** (Ollama) or **Cloud AI** providers")

    # Determine provider type
    ai_type = st.radio(
        "Select AI Type",
        options=["Local AI (Ollama)", "Cloud AI (BYOK)"],
        horizontal=True,
        help="Local AI runs on your machine using Ollama. Cloud AI uses external APIs with your own keys.",
        key="ai_type_radio",
    )

    is_local = ai_type == "Local AI (Ollama)"

    if is_local:
        st.subheader("🖥️ Local AI - Ollama")
        st.info(
            "Ollama runs AI models locally on your machine. "
            "Make sure Ollama is installed and running."
        )

        ollama_url = st.text_input(
            "Ollama Endpoint URL",
            value=st.session_state.get("ollama_url", "http://localhost:11434"),
            help="Default: http://localhost:11434",
            key="ollama_url_input",
        )

        ollama_model = st.selectbox(
            "Select Model",
            options=["llama3", "mistral", "gemma3"],
            index=["llama3", "mistral", "gemma3"].index(
                st.session_state.get("ollama_model", "llama3")
            ),
            help="Choose the Ollama model to use for AI features",
            key="ollama_model_select",
        )

        provider = "ollama"
        model = ollama_model
        api_key = None
        base_url = ollama_url

    else:
        st.subheader("☁️ Cloud AI - Bring Your Own Key")
        st.info(
            "Enter your API keys for cloud AI providers. "
            "Keys are stored only in your session and never saved to disk."
        )

        cloud_provider = st.selectbox(
            "Select Cloud Provider",
            options=["openai", "gemini", "openrouter"],
            index=["openai", "gemini", "openrouter"].index(
                st.session_state.get("cloud_provider", "openai")
            ),
            key="cloud_provider_select",
        )

        provider = cloud_provider

        if cloud_provider == "openai":
            st.markdown("### OpenAI Configuration")
            st.markdown(
                "Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)"
            )
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.get("openai_key", ""),
                help="Your OpenAI API key starting with 'sk-'",
                key="openai_key_input",
            )
            model = st.selectbox(
                "OpenAI Model",
                options=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                index=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"].index(
                    st.session_state.get("openai_model", "gpt-3.5-turbo")
                ),
                key="openai_model_select",
            )
            base_url = None

        elif cloud_provider == "gemini":
            st.markdown("### Gemini Configuration")
            st.markdown(
                "Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)"
            )
            api_key = st.text_input(
                "Gemini API Key",
                type="password",
                value=st.session_state.get("gemini_key", ""),
                help="Your Google Gemini API key",
                key="gemini_key_input",
            )
            model = st.selectbox(
                "Gemini Model",
                options=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
                index=["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"].index(
                    st.session_state.get("gemini_model", "gemini-1.5-flash")
                ),
                key="gemini_model_select",
            )
            base_url = None

        else:  # openrouter
            st.markdown("### OpenRouter Configuration")
            st.markdown(
                "Get your API key from [OpenRouter](https://openrouter.ai/keys)"
            )
            api_key = st.text_input(
                "OpenRouter API Key",
                type="password",
                value=st.session_state.get("openrouter_key", ""),
                help="Your OpenRouter API key",
                key="openrouter_key_input",
            )
            model = st.selectbox(
                "OpenRouter Model",
                options=[
                    "anthropic/claude-3-haiku",
                    "google/gemini-pro",
                    "mistralai/mistral-7b-instruct",
                    "meta-llama/llama-3-8b-instruct",
                ],
                index=[
                    "anthropic/claude-3-haiku",
                    "google/gemini-pro",
                    "mistralai/mistral-7b-instruct",
                    "meta-llama/llama-3-8b-instruct",
                ].index(
                    st.session_state.get("openrouter_model", "anthropic/claude-3-haiku")
                ),
                key="openrouter_model_select",
            )
            openrouter_url = st.text_input(
                "OpenRouter Base URL",
                value=st.session_state.get("openrouter_url", "https://openrouter.ai/api/v1"),
                key="openrouter_url_input",
            )
            base_url = openrouter_url

    # Save / Test Configuration
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔌 Test Connection", width="stretch", type="secondary"):
            if not api_key and not is_local:
                st.error("Please enter an API key for the selected provider.")
            else:
                with st.spinner("Testing connection..."):
                    ai_service = AIService()
                    success, message = ai_service.configure(
                        provider=provider,
                        model=model,
                        api_key=api_key if not is_local else None,
                        base_url=base_url if is_local or provider == "openrouter" else None,
                    )

                    if success:
                        st.success(f"✅ {message}")
                        st.session_state.ai_service = ai_service
                        st.session_state.ai_provider = provider
                        st.session_state.ai_model = model

                        # Save provider/model to DB (not the API key)
                        SettingsRepository.save_settings(
                            provider=provider,
                            model=model,
                        )
                    else:
                        st.error(f"❌ {message}")

    with col2:
        if st.button("💾 Save Configuration", width="stretch", type="primary"):
            # Store in session state
            if is_local:
                st.session_state.ollama_url = ollama_url
                st.session_state.ollama_model = ollama_model
            else:
                st.session_state.cloud_provider = cloud_provider
                if cloud_provider == "openai":
                    st.session_state.openai_key = api_key
                    st.session_state.openai_model = model
                elif cloud_provider == "gemini":
                    st.session_state.gemini_key = api_key
                    st.session_state.gemini_model = model
                elif cloud_provider == "openrouter":
                    st.session_state.openrouter_key = api_key
                    st.session_state.openrouter_model = model
                    st.session_state.openrouter_url = base_url

            # Save provider/model to DB (not the API key)
            SettingsRepository.save_settings(
                provider=provider,
                model=model,
            )

            st.success("✅ Configuration saved to session!")

    # Show current configuration status
    st.divider()
    st.header("📊 Current Configuration")

    if "ai_service" in st.session_state and st.session_state.ai_service.is_configured:
        ai = st.session_state.ai_service
        st.success(f"**Active Provider:** {ai.provider}")
        st.info(f"**Active Model:** {ai.model}")

        # Show appropriate status
        if ai.provider == "ollama":
            st.markdown("🖥️ Using **Local AI** - all data stays on your machine")
        else:
            st.markdown("☁️ Using **Cloud AI** - API calls will be made to the provider")
    else:
        st.warning(
            "⚠️ No AI provider configured. "
            "Please configure and test a provider above to enable AI features."
        )

        # Try to load saved settings from DB
        saved = SettingsRepository.get_settings()
        if saved:
            st.info(f"Saved configuration found: **{saved.provider}/{saved.model}**. "
                    f"Click 'Test Connection' to activate.")

    # About section
    st.divider()
    with st.expander("ℹ️ About AI Providers"):
        st.markdown("""
        ### Local AI (Ollama)
        - Runs completely offline on your machine
        - No data leaves your computer
        - Requires Ollama installation
        - Models: llama3, mistral, gemma3
        
        ### Cloud AI (BYOK)
        - **OpenAI**: Requires API key from platform.openai.com
        - **Gemini**: Requires API key from makersuite.google.com
        - **OpenRouter**: Requires API key from openrouter.ai
        - Your API keys are stored only in session state and never persisted
        
        ### Security
        - API keys are NEVER stored in the database
        - Keys are kept only in your browser session
        - Keys are cleared when you close the browser
        """)