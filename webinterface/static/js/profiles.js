// Profiles & highscores management for songs page
// Extracted from former inline <script> in songs.html to keep markup clean and reusable.
// This file is loaded globally; it initializes itself only when songs page elements are present.

(function(){
    // Cookie helpers (shared)
    function setCookie(name, value, days){
        try{
            const d = new Date();
            d.setTime(d.getTime() + (days*24*60*60*1000));
            document.cookie = `${name}=${encodeURIComponent(value)};expires=${d.toUTCString()};path=/`;
        }catch(e){}
    }
    function getCookie(name){
        try{
            const match = document.cookie.match(new RegExp('(?:^|; )' + name.replace(/([.$?*|{}()\[\]\\\/\+^])/g, '\\$1') + '=([^;]*)'));
            return match ? decodeURIComponent(match[1]) : null;
        }catch(e){ return null; }
    }
    function initProfilesOnSongsPage(){
    const selectEl = document.getElementById('profile_select');
        const inputEl = document.getElementById('profile_name_input');
        const msgEl = document.getElementById('profile_message');
        const createBtn = document.getElementById('create_profile_btn');

        // Guard: only run once per page load and only if songs profile UI exists
        if(!selectEl || !createBtn || createBtn.dataset.profilesInitialized === 'true'){ return; }
        createBtn.dataset.profilesInitialized = 'true';

        function showMsg(text, isError=false){
            if(!msgEl) return;
            msgEl.textContent = text || '';
            msgEl.classList.remove('text-red-400','text-teal-400');
            msgEl.classList.add(isError ? 'text-red-400' : 'text-teal-400');
        }

    function renderSelectWithDeletes(select, profiles, current){
            // Fallback: basic select gets filled with names, separate list renders delete buttons
            select.innerHTML = '';
            profiles.forEach(p=>{
                const opt = document.createElement('option');
                opt.value = p.id;
                opt.textContent = p.name;
                if(current && parseInt(current) === p.id) opt.selected = true;
                select.appendChild(opt);
            });

            // Build an adjacent delete UI list
            let listId = 'profile_delete_list';
            let list = document.getElementById(listId);
            if(!list){
                list = document.createElement('div');
                list.id = listId;
                list.className = 'mt-2 flex flex-wrap gap-2';
                select.parentElement.appendChild(list);
            }
            list.innerHTML = '';
            profiles.forEach(p=>{
                const pill = document.createElement('div');
                pill.className = 'inline-flex items-center bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm';
                const name = document.createElement('span');
                name.textContent = p.name;
                name.className = 'mr-2';
                const del = document.createElement('button');
                del.title = 'Delete profile';
                del.setAttribute('aria-label', 'Delete profile');
                del.className = 'text-red-500 hover:text-red-600 font-bold px-1';
                del.textContent = '×';
                del.addEventListener('click', ()=>{
                    const confirmMsg = `Delete profile "${p.name}"? This will remove highscores for this profile.`;
                    if(!window.confirm(confirmMsg)) return;
                    fetch('/api/delete_profile', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({profile_id: p.id})})
                        .then(r=>r.json())
                        .then(resp=>{
                            if(resp.success){
                                showMsg('Profile deleted');
                                // If we deleted the current one, clear and pick another
                                if(window.currentProfileId == p.id){ window.currentProfileId = null; }
                                loadProfiles();
                                if(typeof get_songs === 'function') get_songs();
                            } else {
                                showMsg(resp.error || 'Failed to delete profile', true);
                            }
                        })
                        .catch(()=>showMsg('Network error deleting profile', true));
                });
                pill.appendChild(name);
                pill.appendChild(del);
                list.appendChild(pill);
            });
        }

    function loadProfiles(){
            fetch('/api/get_profiles')
                .then(r=>r.json())
                .then(data=>{
            let current = window.currentProfileId || getCookie('currentProfileId');
                    const profiles = data.profiles || [];
                    if(profiles.length === 0){
                        selectEl.innerHTML = '';
                        const opt = document.createElement('option');
                        opt.textContent = 'No profiles';
                        opt.value='';
                        selectEl.appendChild(opt);
                        showMsg('Create a profile to start tracking highscores.');
                        return;
                    }
                    renderSelectWithDeletes(selectEl, profiles, current);
                    if(current && profiles.some(p=>p.id === parseInt(current))){
                        window.currentProfileId = parseInt(current);
                        setCookie('currentProfileId', window.currentProfileId, 365);
                        fetch('/api/set_current_profile', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({profile_id: window.currentProfileId})}).catch(()=>{});
                        if(typeof get_songs === 'function') get_songs();
                    } else if(!window.currentProfileId && profiles[0]){
                        window.currentProfileId = profiles[0].id;
                        setCookie('currentProfileId', window.currentProfileId, 365);
                        fetch('/api/set_current_profile', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({profile_id: window.currentProfileId})}).catch(()=>{});
                        if(typeof get_songs === 'function') get_songs();
                    }
                    showMsg('Profiles loaded');
                })
                .catch(()=>showMsg('Failed to load profiles', true));
        }

        function createProfile(){
            const name = (inputEl.value || '').trim();
            if(!name){
                showMsg('Enter a profile name', true);
                inputEl.focus();
                return;
            }
            fetch('/api/create_profile', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({name})
            }).then(r=>r.json())
              .then(resp=>{
                  if(resp.success){
                      window.currentProfileId = resp.profile.id;
                      setCookie('currentProfileId', window.currentProfileId, 365);
                      showMsg('Profile created');
                      inputEl.value='';
                      // Sync selection to backend
                      fetch('/api/set_current_profile', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({profile_id: window.currentProfileId})}).catch(()=>{});
                      loadProfiles();
                      if(typeof get_songs === 'function') get_songs();
                  } else {
                      showMsg(resp.error || 'Error creating profile', true);
                  }
              })
              .catch(()=>showMsg('Network error creating profile', true));
        }

        // Expose for other scripts if needed
        window.loadProfiles = loadProfiles;
        window.createProfile = createProfile;

        createBtn.addEventListener('click', createProfile);
        inputEl.addEventListener('keyup', (e)=>{ if(e.key==='Enter'){ createProfile(); }});
        selectEl.addEventListener('change', function(){
            window.currentProfileId = this.value || null;
            if(window.currentProfileId){ setCookie('currentProfileId', window.currentProfileId, 365); }
            // Sync selection to backend (null or id)
            fetch('/api/set_current_profile', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({profile_id: window.currentProfileId})}).catch(()=>{});
            if(this.value){
                showMsg('Selected profile: ' + this.options[this.selectedIndex].text);
                if(typeof get_songs === 'function') get_songs();
            }
        });

        loadProfiles();
    }

    // Run after each dynamic page load (index.js calls initialize_songs which will invoke this)
    window.initProfilesOnSongsPage = initProfilesOnSongsPage;

    // Also attempt immediate init in case songs page is the initial load
    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', initProfilesOnSongsPage);
    } else {
        initProfilesOnSongsPage();
    }
})();
// profiles.js - handles user profiles and highscores on songs page
(function(){
    console.log('[Profiles] profiles.js loaded');
    const state = {
        selectEl: null,
        inputEl: null,
        msgEl: null,
        createBtn: null
    };

    function showMsg(text, isError=false){
        if(!state.msgEl) return;
        state.msgEl.textContent = text || '';
        state.msgEl.classList.remove('text-red-400','text-teal-400');
        state.msgEl.classList.add(isError ? 'text-red-400' : 'text-teal-400');
    }

    function loadProfiles(){
        if(!state.selectEl){
            console.warn('[Profiles] loadProfiles called before init');
            return;
        }
        fetch('/api/get_profiles')
            .then(r=>r.json())
            .then(data=>{
                const current = window.currentProfileId;
                const profiles = data.profiles || [];
                if(profiles.length === 0){
                    state.selectEl.innerHTML = '';
                    const opt = document.createElement('option');
                    opt.textContent = 'No profiles';
                    opt.value='';
                    state.selectEl.appendChild(opt);
                    showMsg('Create a profile to start tracking highscores.');
                    return;
                }
                // Reuse renderer from the other IIFE if present
                if(typeof window.loadProfiles === 'function'){
                    // call the other loader to render deletes UI too
                    try { window.loadProfiles(); return; } catch(e) {}
                }
                // Basic fallback
                state.selectEl.innerHTML = '';
                profiles.forEach(p=>{
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = p.name;
                    if(current && parseInt(current) === p.id) opt.selected = true;
                    state.selectEl.appendChild(opt);
                });
                let cookieCurrent = window.currentProfileId || getCookie('currentProfileId');
                if(cookieCurrent && profiles.some(p=>p.id === parseInt(cookieCurrent))){
                    window.currentProfileId = parseInt(cookieCurrent);
                    setCookie('currentProfileId', window.currentProfileId, 365);
                    fetch('/api/set_current_profile', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({profile_id: window.currentProfileId})}).catch(()=>{});
                } else if(!window.currentProfileId && profiles[0]){
                    window.currentProfileId = profiles[0].id;
                    setCookie('currentProfileId', window.currentProfileId, 365);
                    fetch('/api/set_current_profile', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({profile_id: window.currentProfileId})}).catch(()=>{});
                }
                showMsg('Profiles loaded');
            })
            .catch(()=>showMsg('Failed to load profiles', true));
    }

    function createProfile(){
        console.log('[Profiles] createProfile invoked');
        const name = (state.inputEl && state.inputEl.value || '').trim();
        if(!name){
            showMsg('Enter a profile name', true);
            state.inputEl && state.inputEl.focus();
            return;
        }
        fetch('/api/create_profile', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({name})
        }).then(r=>r.json())
          .then(resp=>{
              if(resp.success){
                  window.currentProfileId = resp.profile.id;
                  setCookie('currentProfileId', window.currentProfileId, 365);
                  showMsg('Profile created');
                  if(state.inputEl) state.inputEl.value='';
                  fetch('/api/set_current_profile', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({profile_id: window.currentProfileId})}).catch(()=>{});
                  loadProfiles();
                  if(typeof get_songs === 'function') get_songs();
              } else {
                  showMsg(resp.error || 'Error creating profile', true);
              }
          })
          .catch(()=>showMsg('Network error creating profile', true));
    }

    function attachEvents(){
        if(state.createBtn){
            state.createBtn.addEventListener('click', createProfile);
        }
        if(state.inputEl){
            state.inputEl.addEventListener('keyup', e=>{ if(e.key==='Enter') createProfile(); });
        }
        if(state.selectEl){
            state.selectEl.addEventListener('change', function(){
                window.currentProfileId = this.value || null;
                if(window.currentProfileId){ setCookie('currentProfileId', window.currentProfileId, 365); }
                fetch('/api/set_current_profile', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({profile_id: window.currentProfileId})}).catch(()=>{});
                if(this.value){
                    showMsg('Selected profile: ' + this.options[this.selectedIndex].text);
                    if(typeof get_songs === 'function') get_songs();
                }
            });
        }
    }

    function init(){
        state.selectEl = document.getElementById('profile_select');
        state.inputEl = document.getElementById('profile_name_input');
        state.msgEl = document.getElementById('profile_message');
        state.createBtn = document.getElementById('create_profile_btn');
        if(!state.selectEl || !state.createBtn){
            console.warn('[Profiles] Elements not found on this page; init skipped');
            return;
        }
        attachEvents();
    loadProfiles();
        console.log('[Profiles] Init complete');
    }

    if(document.readyState === 'loading'){
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    window._profiles = {
        createProfile,
        loadProfiles
    };
})();
