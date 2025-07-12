# streamlit_fix.py
"""
Streamlit compatibility fixes - IMPORT THIS FIRST in your app.py
"""

import streamlit as st

def fix_streamlit_compatibility():
    """
    Fix Streamlit compatibility issues for older versions
    """
    
    # Fix 1: st.cache_data (added in Streamlit 1.18.0)
    if not hasattr(st, 'cache_data'):
        print("Warning: st.cache_data not found, using st.cache fallback")
        st.cache_data = st.cache
    
    # Fix 2: st.cache_resource (added in Streamlit 1.18.0) 
    if not hasattr(st, 'cache_resource'):
        print("Warning: st.cache_resource not found, using st.cache fallback")
        def cache_resource_fallback(**kwargs):
            kwargs['allow_output_mutation'] = True
            return st.cache(**kwargs)
        st.cache_resource = cache_resource_fallback
    
    # Fix 3: st.session_state (added in Streamlit 0.84.0)
    if not hasattr(st, 'session_state'):
        print("Warning: st.session_state not found, creating fallback")
        class SessionState:
            def __init__(self):
                self._state = {}
            
            def __getattr__(self, name):
                return self._state.get(name, None)
            
            def __setattr__(self, name, value):
                if name.startswith('_'):
                    super().__setattr__(name, value)
                else:
                    self._state[name] = value
                    
            def __contains__(self, key):
                return key in self._state
            
            def get(self, key, default=None):
                return self._state.get(key, default)
            
            def keys(self):
                return self._state.keys()
            
            def items(self):
                return self._state.items()
            
            def values(self):
                return self._state.values()
            
            def pop(self, key, default=None):
                return self._state.pop(key, default)
            
            def clear(self):
                self._state.clear()
        
        st.session_state = SessionState()
    
    # Fix 4: st.rerun (added in Streamlit 1.27.0)
    if not hasattr(st, 'rerun'):
        if hasattr(st, 'experimental_rerun'):
            st.rerun = st.experimental_rerun
        else:
            print("Warning: No rerun method available")
            def dummy_rerun():
                pass
            st.rerun = dummy_rerun
    
    # Fix 5: st.tabs (added in Streamlit 1.11.0)
    if not hasattr(st, 'tabs'):
        def tabs_fallback(tab_names):
            """Fallback for st.tabs using selectbox"""
            selected_tab = st.selectbox("Select tab:", tab_names)
            
            class TabContext:
                def __init__(self, name, selected):
                    self.name = name
                    self.selected = selected
                
                def __enter__(self):
                    return self
                
                def __exit__(self, *args):
                    pass
            
            return [TabContext(name, name == selected_tab) for name in tab_names]
        
        st.tabs = tabs_fallback
    
    # Fix 6: st.columns (added in Streamlit 0.68.0)
    if not hasattr(st, 'columns'):
        if hasattr(st, 'beta_columns'):
            st.columns = st.beta_columns
        else:
            print("Warning: No columns method available")
            def dummy_columns(spec):
                return [st.container() for _ in range(len(spec) if isinstance(spec, list) else spec)]
            st.columns = dummy_columns
    
    # Fix 7: st.container (added in Streamlit 0.69.0)
    if not hasattr(st, 'container'):
        if hasattr(st, 'beta_container'):
            st.container = st.beta_container
        else:
            class DummyContainer:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
            def dummy_container():
                return DummyContainer()
            st.container = dummy_container
    
    # Fix 8: st.expander (added in Streamlit 0.70.0)
    if not hasattr(st, 'expander'):
        if hasattr(st, 'beta_expander'):
            st.expander = st.beta_expander
        else:
            def dummy_expander(label, expanded=False):
                if expanded or st.checkbox(f"Expand {label}"):
                    return st.container()
                else:
                    class DummyExpander:
                        def __enter__(self):
                            return st.empty()
                        def __exit__(self, *args):
                            pass
                    return DummyExpander()
            st.expander = dummy_expander
    
    # Fix 9: st.form (added in Streamlit 0.81.0)
    if not hasattr(st, 'form'):
        def dummy_form(key, clear_on_submit=False):
            class DummyForm:
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    pass
            return DummyForm()
        st.form = dummy_form
        
        # Also need form_submit_button
        if not hasattr(st, 'form_submit_button'):
            st.form_submit_button = st.button
    
    # Fix 10: st.metric (added in Streamlit 1.0.0)
    if not hasattr(st, 'metric'):
        def dummy_metric(label, value, delta=None):
            if delta is not None:
                st.write(f"**{label}**: {value} (Δ {delta})")
            else:
                st.write(f"**{label}**: {value}")
        st.metric = dummy_metric
    
    print(f"Streamlit compatibility fixes applied for version {st.__version__}")

# Apply fixes immediately when imported
fix_streamlit_compatibility()