"""
Streamlit Web App for American Padel Tournament Calendar Generation.

This app provides a mobile-friendly interface to generate tournament calendars
using the genetic algorithm optimizer.

Run locally with: uv run streamlit run streamlit_app.py
"""

import streamlit as st
import time
import re
from src.genetic_algorithm import GeneticAlgorithm, validate_solution, detect_cut_points
from src.printer import match_vector_to_string
from src.dataclasses import Calendar


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="🎾 American Tournament",
    page_icon="🎾",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# CUSTOM CSS FOR MOBILE-FRIENDLY DESIGN
# =============================================================================

st.markdown("""
<style>
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    
    /* Title styling */
    h1 {
        text-align: center;
        color: #1E88E5;
        font-size: 2rem !important;
    }
    
    /* Match card - FIXED CONTRAST */
    .match-card {
        background: #1a1a2e;
        border-left: 4px solid #4CAF50;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        font-family: 'Courier New', monospace;
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    .match-card strong {
        color: #4CAF50;
    }
    
    /* Round header */
    .round-header {
        background: #1E88E5;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin-top: 1rem;
        font-weight: bold;
    }
    
    /* Cut point badge */
    .cut-badge {
        display: inline-block;
        background: #4CAF50;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    
    .cut-badge-acceptable {
        background: #FF9800;
    }
    
    /* Success message */
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Progress info */
    .progress-info {
        background: #2d2d44;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        color: #ffffff;
        font-family: monospace;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_player_name(index: int, custom_names: list = None) -> str:
    """Convert player index to name. Uses custom name if provided, else letter."""
    if custom_names and index < len(custom_names) and custom_names[index].strip():
        return custom_names[index].strip()
    return chr(ord('A') + index)


def replace_letters_with_names(text: str, n_players: int, custom_names: list = None) -> str:
    """Replace player letters (A, B, C...) with custom names in text.
    
    Uses word boundaries to only replace standalone letters, not letters within names.
    """
    if not custom_names:
        return text
    
    result = text
    # Replace each letter with its custom name using word boundaries
    for i in range(n_players):
        letter = chr(ord('A') + i)
        name = get_player_name(i, custom_names)
        if name != letter:  # Only replace if there's a custom name
            # Use regex to match standalone letter (surrounded by non-word chars or string boundaries)
            pattern = r'(?<![A-Za-z])' + letter + r'(?![A-Za-z])'
            result = re.sub(pattern, name, result)
    return result


def calendar_to_csv(calendar: Calendar, custom_names: list = None) -> str:
    """Convert calendar to CSV string for download."""
    n_players = calendar.n_players
    n_courts = calendar.n_courts
    
    perfect_cuts, acceptable_cuts = detect_cut_points(calendar)
    
    lines = ["Round,Court,Match,Team 1,Team 2,Perfect Cut,Acceptable Cut"]
    
    for i in range(len(calendar)):
        match = calendar.get_match(i)
        match_num = i + 1
        round_num = calendar.get_round_for_match(i)
        court_num = (i % n_courts) + 1
        
        team1, team2 = match.get_teams()
        team1_str = " & ".join([get_player_name(p, custom_names) for p in team1])
        team2_str = " & ".join([get_player_name(p, custom_names) for p in team2])
        
        # Check if this position is a cut point (end of round)
        is_end_of_round = (i + 1) % n_courts == 0
        perfect = "✓" if is_end_of_round and round_num in perfect_cuts else ""
        acceptable = "✓" if is_end_of_round and round_num in acceptable_cuts else ""
        
        lines.append(f"{round_num},{court_num},{match_num},{team1_str},{team2_str},{perfect},{acceptable}")
    
    return "\n".join(lines)


def format_match_with_names(match_vector, n_players: int, custom_names: list = None) -> str:
    """Format match with custom player names."""
    base_str = match_vector_to_string(match_vector, n_players)
    return replace_letters_with_names(base_str, n_players, custom_names)


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    # Header
    st.markdown("# 🎾 American Tournament")
    st.markdown("<p style='text-align: center; color: #666;'>Optimized calendar generator for padel/tennis</p>", unsafe_allow_html=True)
    
    # ==========================================================================
    # CONFIGURATION SECTION
    # ==========================================================================
    
    st.markdown("---")
    st.markdown("### ⚙️ Tournament Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_players = st.slider(
            "👥 Players",
            min_value=4,
            max_value=16,
            value=8,
            step=1,
            help="Total number of players in the tournament"
        )
    
    with col2:
        n_courts = st.slider(
            "🎾 Courts",
            min_value=1,
            max_value=4,
            value=2,
            step=1,
            help="Number of available courts"
        )
    
    # Validate minimum players for courts
    min_players = n_courts * 4
    if n_players < min_players:
        st.warning(f"⚠️ With {n_courts} court(s) you need at least {min_players} players")
        n_players = min_players
    
    n_rounds = st.slider(
        "🔄 Rounds",
        min_value=3,
        max_value=30,
        value=10,
        step=1,
        help="Number of rounds to play"
    )
    
    total_matches = n_rounds * n_courts
    
    # Show summary
    st.markdown(f"""
    <div style='background: #e3f2fd; padding: 1rem; border-radius: 10px; margin: 1rem 0; color: #1a1a2e;'>
        <strong>📊 Summary:</strong><br>
        • {n_players} players<br>
        • {n_courts} court(s)<br>
        • {n_rounds} rounds<br>
        • <strong>{total_matches} total matches</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # ==========================================================================
    # PLAYER NAMES (OPTIONAL)
    # ==========================================================================
    
    with st.expander("👤 Player names (optional)"):
        st.markdown("_Leave blank to use letters (A, B, C...)_")
        
        custom_names = []
        cols = st.columns(2)
        for i in range(n_players):
            col_idx = i % 2
            with cols[col_idx]:
                default_letter = chr(ord('A') + i)
                name = st.text_input(
                    f"Player {default_letter}",
                    value="",
                    key=f"player_name_{i}",
                    placeholder=f"E.g.: John, Mary..."
                )
                custom_names.append(name)
    
    # ==========================================================================
    # ADVANCED OPTIONS (COLLAPSED)
    # ==========================================================================
    
    with st.expander("🔧 Advanced options"):
        col1, col2 = st.columns(2)
        
        with col1:
            population_size = st.select_slider(
                "Population size",
                options=[50, 100, 150, 200],
                value=100,
                help="Higher = better quality, slower"
            )
        
        with col2:
            generations = st.select_slider(
                "Generations",
                options=[100, 150, 200, 300],
                value=200,
                help="Algorithm iterations"
            )
        
        mutation_rate = st.slider(
            "Mutation rate",
            min_value=0.05,
            max_value=0.30,
            value=0.20,
            step=0.05,
            help="0.20 = more cut points"
        )
    
    # ==========================================================================
    # GENERATE BUTTON
    # ==========================================================================
    
    st.markdown("---")
    
    if st.button("🚀 GENERATE CALENDAR", use_container_width=True, type="primary"):
        
        # Initialize GA
        ga = GeneticAlgorithm(
            n_players=n_players,
            n_rounds=n_rounds,
            n_courts=n_courts,
            population_size=population_size,
            generations=generations,
            mutation_rate=mutation_rate,
            crossover_rate=0.8,
            elitism_size=2,
            weight_balance=100.0,
            weight_opponent_rep=10.0,
            weight_team_rep=10.0,
            weight_waiting=5.0,
            weight_early_cut=75.0,
            n_jobs=-1,
            early_stopping_patience=50,
        )
        
        # Progress display
        progress_container = st.container()
        with progress_container:
            st.markdown("### 🧬 Optimizing calendar...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            metrics_placeholder = st.empty()
        
        # Variables to track progress
        start_time = time.time()
        
        def update_progress(gen, total_gen, best_fit, avg_fit):
            """Callback to update Streamlit UI with progress."""
            progress = gen / total_gen
            progress_bar.progress(progress)
            
            elapsed = time.time() - start_time
            
            status_text.markdown(f"""
            <div class='progress-info'>
                🔄 <strong>Generation {gen}/{total_gen}</strong> | 
                ⏱️ {elapsed:.1f}s | 
                📈 Fitness: {best_fit:.0f}
            </div>
            """, unsafe_allow_html=True)
            
            return True  # Continue evolution
        
        # Run optimization with progress callback
        best_calendar = ga.run(verbose=False, progress_callback=update_progress)
        
        elapsed_time = time.time() - start_time
        
        # Final progress update
        progress_bar.progress(100)
        status_text.markdown(f"""
        <div class='progress-info' style='background: #1b5e20;'>
            ✅ <strong>Completed!</strong> | 
            {len(ga.best_fitness_history)} generations | 
            {elapsed_time:.1f}s
        </div>
        """, unsafe_allow_html=True)
        
        # Validate
        is_valid, quality, message = validate_solution(best_calendar)
        
        # Store results in session state
        st.session_state['calendar'] = best_calendar
        st.session_state['is_valid'] = is_valid
        st.session_state['quality'] = quality
        st.session_state['n_players'] = n_players
        st.session_state['custom_names'] = custom_names
        st.session_state['elapsed_time'] = elapsed_time
        st.session_state['generations_run'] = len(ga.best_fitness_history)
        
        time.sleep(0.5)  # Brief pause to show completion
        st.rerun()
    
    # ==========================================================================
    # DISPLAY RESULTS (if available)
    # ==========================================================================
    
    if 'calendar' in st.session_state:
        calendar = st.session_state['calendar']
        is_valid = st.session_state['is_valid']
        quality = st.session_state['quality']
        n_players = st.session_state['n_players']
        custom_names = st.session_state.get('custom_names', [])
        elapsed_time = st.session_state.get('elapsed_time', 0)
        generations_run = st.session_state.get('generations_run', 0)
        
        st.markdown("---")
        
        # Success/Warning message
        if is_valid:
            st.markdown(f"""
            <div class='success-box'>
                <h3 style='margin: 0;'>✅ Calendar generated!</h3>
                <p style='margin: 0.5rem 0 0 0;'>Quality: {quality} | {generations_run} generations | {elapsed_time:.1f}s</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"⚠️ Calendar generated with quality: {quality}")
        
        # =======================================================================
        # CUT POINTS SECTION (MOST IMPORTANT FOR USERS)
        # =======================================================================
        
        st.markdown("### ✂️ Cut Points")
        st.markdown("<small>Rounds where you can stop with all players balanced</small>", unsafe_allow_html=True)
        
        perfect_cuts, acceptable_cuts = detect_cut_points(calendar)
        
        if perfect_cuts:
            st.markdown("**🟢 Perfect cuts** (all equal):")
            cuts_html = " ".join([f"<span class='cut-badge'>Round {r}</span>" for r in perfect_cuts[:10]])
            if len(perfect_cuts) > 10:
                cuts_html += f" <small>+{len(perfect_cuts)-10} more</small>"
            st.markdown(cuts_html, unsafe_allow_html=True)
        
        acceptable_only = [c for c in acceptable_cuts if c not in perfect_cuts]
        if acceptable_only:
            st.markdown("**🟡 Acceptable cuts** (max difference: 1 match):")
            cuts_html = " ".join([f"<span class='cut-badge cut-badge-acceptable'>Round {r}</span>" for r in acceptable_only[:8]])
            st.markdown(cuts_html, unsafe_allow_html=True)
        
        # =======================================================================
        # STATISTICS
        # =======================================================================
        
        st.markdown("### 📊 Statistics")
        
        matches_per_player = calendar.get_matches_per_player()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Matches", len(calendar))
        
        with col2:
            min_matches = min(matches_per_player.values())
            max_matches = max(matches_per_player.values())
            st.metric("Matches/Player", f"{min_matches}-{max_matches}")
        
        with col3:
            st.metric("Cut Points", len(perfect_cuts))
        
        # Player stats table
        with st.expander("📋 Player details"):
            stats_data = []
            for player_idx in sorted(matches_per_player.keys()):
                player_name = get_player_name(player_idx, custom_names)
                matches = matches_per_player[player_idx]
                stats_data.append({"Player": player_name, "Matches": matches})
            
            st.dataframe(stats_data, use_container_width=True, hide_index=True)
        
        # =======================================================================
        # CALENDAR DISPLAY
        # =======================================================================
        
        st.markdown("### 📅 Match Calendar")
        
        n_courts = calendar.n_courts
        total_rounds = calendar.get_total_rounds()
        
        for round_num in range(1, total_rounds + 1):
            # Check if this round is a cut point
            cut_marker = ""
            if round_num in perfect_cuts:
                cut_marker = " ✂️🟢"
            elif round_num in acceptable_cuts:
                cut_marker = " ✂️🟡"
            
            st.markdown(f"<div class='round-header'>📅 Round {round_num}{cut_marker}</div>", unsafe_allow_html=True)
            
            matches_in_round = calendar.get_matches_in_round(round_num)
            
            for court_idx, match_idx in enumerate(matches_in_round):
                match = calendar.get_match(match_idx)
                match_str = format_match_with_names(match.match_vector, n_players, custom_names)
                court_label = f"<strong>Court {court_idx + 1}:</strong> " if n_courts > 1 else ""
                
                st.markdown(f"""
                <div class='match-card'>
                    {court_label}{match_str}
                </div>
                """, unsafe_allow_html=True)
        
        # =======================================================================
        # DOWNLOAD BUTTON
        # =======================================================================
        
        st.markdown("---")
        
        csv_content = calendar_to_csv(calendar, custom_names)
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_content,
            file_name="american_tournament.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Clear button
        if st.button("🔄 New calendar", use_container_width=True):
            for key in ['calendar', 'is_valid', 'quality', 'n_players', 'custom_names', 'elapsed_time', 'generations_run']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # ==========================================================================
    # FOOTER
    # ==========================================================================
    
    st.markdown("---")
    st.markdown("""
    <p style='text-align: center; color: #999; font-size: 0.8rem;'>
        🎾 American Tournament Generator v2.1<br>
        Powered by Genetic Algorithms
    </p>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
