# ... [Previous code for Success/Fail buttons remains the same] ...
            c1, c2 = st.columns(2)
            if c1.button("✅ Success", use_container_width=True):
                if is_last: st.session_state.winner = player
                else: 
                    st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                    st.session_state.rolled = False
                st.rerun()
            if c2.button("❌ Fail", use_container_width=True):
                player['pos'] = player['prev']
                st.session_state.turn = (st.session_state.turn + 1) % st.session_state.num_players
                st.session_state.rolled = False
                st.rerun()

            # --- UPDATED: VIEW ANSWERS FOR ALL QUESTIONS ---
            with st.expander("👁️ View Answers"):
                if "both" in task_text.lower():
                    # Specialized logic for Club Connections
                    match = re.search(r"both (.*?) & (.*)", task_text)
                    if match:
                        c1_name, c2_name = match.group(1).strip(), match.group(2).strip()
                        ans_list = fetch_shared_players(c1_name, c2_name)
                        if ans_list: 
                            st.write(", ".join(ans_list[:15])) # Limit to top 15 for readability
                        else: 
                            st.info("No common players found in quick-lookup. Try the link below.")
                    
                # Generic Search link for all other tasks (Stadiums, Stats, Trophies, etc.)
                search_query = task_text.replace("Name a", "").strip()
                st.markdown(f"""
                <a href="https://www.google.com/search?q=football+{search_query.replace(' ', '+')}" target="_blank" style="text-decoration:none;">
                    <div style="background:#333; color:white; padding:10px; border-radius:5px; text-align:center; font-size:0.8rem; border:1px solid #555;">
                        🔍 Search for Answers
                    </div>
                </a>
                """, unsafe_allow_html=True)

        st.markdown("---")
        # ... [Rest of the reset/end game logic remains the same] ...
