/**
 * Refactored JavaScript Script for Texture Packs filtering, searching, and pagination.
 */
(function() {
    'use strict';

    // --- CONFIGURATION AND GLOBAL VARIABLES ---
    let currentPage = 1;
    // Set this to 10 if you want 2 columns * 5 rows on each page.
    const cardsPerPage = 10; 
    let texturePacks = []; 
    let filteredPacks = [];

    const DISCORD_INVITE = 'https://discord.gg/YMGPn26WMN';

    // --- DOM ELEMENTS ---
    const cardsContainer = document.getElementById("cards-container");
    const searchInput = document.getElementById("search");
    const filterResolutionSelect = document.getElementById("filterResolution"); 
    const filterTypeSelect = document.getElementById("filterType"); 
    const filterFeaturedSelect = document.getElementById("filterFeatured"); 
    const pagination = document.getElementById("pagination");
    const popup = document.getElementById("popup");
    const popupBox = popup.querySelector(".popup-box");
    const addPackBtn = document.getElementById("addPackBtn");
    const invitePopup = document.getElementById("invite-popup");
    const inviteCloseBtn = invitePopup.querySelector('.close-invite-btn');

    // ----------------------------------------------------
    // --- UTILITY FUNCTIONS ---
    // ----------------------------------------------------

    /**
     * Formats an array of creators into an HTML link string.
     * @param {string[]} creatorsArray 
     * @returns {string} Formatted string with anchors.
     */
    function formatCreators(creatorsArray) {
        if (!Array.isArray(creatorsArray) || creatorsArray.length === 0) {
            return "Unknown";
        }
        
        const links = creatorsArray.map(name => 
            `<a href="creator-detail.html?creator=${encodeURIComponent(name)}" target="_blank">${name}</a>`
        );
        
        if (links.length === 1) {
            return links[0];
        }

        const last = links.pop();
        return links.join(', ') + ' & ' + last;
    }

    /**
     * Returns a lowercase string of concatenated creator names for searching.
     * @param {string[]} creatorsArray 
     * @returns {string} 
     */
    function getCreatorsString(creatorsArray) {
        if (!Array.isArray(creatorsArray)) return '';
        return creatorsArray.join(', ').toLowerCase();
    }

    /**
     * Initiates a download from a given URL.
     * @param {string} downloadUrl 
     */
    function initiateDownload(downloadUrl) {
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = '';
        document.body.appendChild(link);
        link.click();
        setTimeout(() => link.remove(), 100); 
    }
    
    // ----------------------------------------------------
    // --- DATA LOADING AND INITIALIZATION ---
    // ----------------------------------------------------
    
    /**
     * Fetches texture pack data from the JSON file.
     */
    async function fetchPacks() {
        try {
            const res = await fetch("data/data.json"); 
            
            if (!res.ok) {
                cardsContainer.innerHTML = "<p>Error loading packs. Please check the console.</p>";
                return;
            }
            
            const data = await res.json();
            texturePacks = data; // Assumes data is the array of packs
            
            filterAndSortPacks(); // Initial render
            
        } catch (err) {
            console.error('Error fetching packs from data/data.json:', err);
            cardsContainer.innerHTML = "<p>Failed to load data. Please check the console.</p>";
        }
    }
    
    // ----------------------------------------------------
    // --- FILTER AND SORT LOGIC ---
    // ----------------------------------------------------

    /**
     * Applies all search and selection filters.
     */
    function filterAndSortPacks() {
        const fullText = searchInput.value.toLowerCase();
        const resolution = filterResolutionSelect.value;
        const type = filterTypeSelect.value;
        const featured = filterFeaturedSelect.value;

        let searchText = fullText;
        let creatorFilter = '';

        // Logic to extract 'by:' filter
        const creatorMatch = fullText.match(/by:\s*([a-z0-9_.-]+)/); 
        if (creatorMatch && creatorMatch[1]) {
            creatorFilter = creatorMatch[1].trim(); 
            searchText = fullText.replace(creatorMatch[0], '').trim(); 
        }

        filteredPacks = texturePacks.filter(pack => {
            if (!pack.name || !Array.isArray(pack.creators)) return false; 

            const packName = pack.name.toLowerCase();
            const packCreatorsString = getCreatorsString(pack.creators); 

            // 1. Text and Creator Filter
            const matchesText = searchText === '' || packName.includes(searchText);
            const matchesCreator = creatorFilter === '' || packCreatorsString.includes(creatorFilter);

            // 2. Resolution Filter
            const matchesResolution = resolution === "all" || (
                Array.isArray(pack.resolution) && pack.resolution.includes(resolution)
            );

            // 3. Type Filter
            const packType = String(pack.type || '').toLowerCase();
            const matchesType = type === "all" || (packType === type);

            // 4. Featured Filter
            const matchesFeatured = featured === "all" || (pack.featured === true);
            
            return matchesText && matchesCreator && matchesResolution && matchesType && matchesFeatured; 
        });

        // Ordering is currently skipped (sortPacks in original was empty)
        // const sortedAndFiltered = sortPacks(filteredPacks, ''); 

        // Reset page and render
        currentPage = 1; 
        renderCards(filteredPacks);
    }
    
    // ----------------------------------------------------
    // --- RENDERING FUNCTIONS ---
    // ----------------------------------------------------

    /**
     * Creates and renders the texture pack cards for the current page.
     * @param {object[]} list Filtered/sorted list of packs.
     */
    function renderCards(list) {
        cardsContainer.innerHTML = "";
        
        const start = (currentPage - 1) * cardsPerPage;
        const end = start + cardsPerPage;
        const pageItems = list.slice(start, end);
        
        // Adjust page if no items are found on the current page
        if (pageItems.length === 0 && list.length > 0 && currentPage !== 1) {
            currentPage = 1; 
            renderCards(list); 
            return;
        }

        if (list.length === 0) {
            cardsContainer.innerHTML = `<p class="no-results-message">No packs found matching the selected filters.</p>`;
        }
        
        pageItems.forEach(pack => {
            const card = document.createElement("div");
            card.classList.add("card");
            card.dataset.id = pack.id; 

            const isFeatured = pack.featured === true;
            const featuredTitleClass = isFeatured ? 'featured-title' : '';
            const featuredStar = isFeatured ? '<span class="featured-star">★ </span>' : '';
            const featuredIconClass = isFeatured ? 'featured-icon-glow' : ''; 
            const creatorsFormatted = formatCreators(pack.creators);
            
            card.innerHTML = `
                <div class="card-top">
                    <img src="${pack.icon}" alt="Pack Icon" class="card-icon ${featuredIconClass}">
                    <div class="card-content">
                        <h3 class="${featuredTitleClass}">
                            ${featuredStar}
                            <a href="pack-detail.html?id=${pack.id}" target="_self">${pack.name}</a> 
                            by ${creatorsFormatted} - ${pack.version}
                        </h3>
                        <p class="pack-description-text">${pack.description}</p>
                        <button class="download-btn" data-url="${pack.download}">Download (${pack.version})</button>
                        <p class="download-count"><small>Available for Download</small></p>
                        <button class="more-info" aria-label="More information about ${pack.name}">i</button>
                    </div>
                </div>
                <img src="${pack.screenshot}" alt="Pack Screenshot" class="card-screenshot">
            `;

            cardsContainer.appendChild(card);

            // Add event listeners
            card.querySelector(".download-btn").addEventListener("click", () => initiateDownload(pack.download));
            card.querySelector(".more-info").addEventListener("click", () => openPopup(pack));
        });

        renderPagination(list);
        
        // Scroll to top of the content area for better UX on page change
        const topBar = document.querySelector(".title");
        if (topBar) {
            topBar.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    /**
     * Renders the pagination buttons.
     * @param {object[]} list Filtered/sorted list of packs.
     */
    function renderPagination(list) {
        pagination.innerHTML = "";

        const totalPages = Math.ceil(list.length / cardsPerPage);
        if (totalPages <= 1) return;

        // Previous button
        const prev = document.createElement("button");
        prev.textContent = "Prev";
        prev.disabled = currentPage === 1;
        prev.onclick = () => { currentPage--; renderCards(list); }; 
        pagination.appendChild(prev);

        // Page buttons
        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement("button");
            btn.textContent = i;
            if (i === currentPage) btn.classList.add("active-page");
            btn.onclick = () => { currentPage = i; renderCards(list); };
            pagination.appendChild(btn);
        }

        // Next button
        const next = document.createElement("button");
        next.textContent = "Next";
        next.disabled = currentPage === totalPages;
        next.onclick = () => { currentPage++; renderCards(list); };
        pagination.appendChild(next);
    }
    
    /**
     * Opens and populates the details popup.
     * @param {object} pack The texture pack data object.
     */
    function openPopup(pack) {
        popupBox.dataset.id = pack.id;

        const resolutionDisplay = Array.isArray(pack.resolution) ? pack.resolution.join(', ') : pack.resolution;
        const creatorsFormatted = formatCreators(pack.creators);
        
        popupBox.innerHTML = `
            <div class="popup-top">
                <img src="${pack.icon}" alt="Pack Icon" class="pack-icon"> 

                <div class="popup-info">
                    <h2 class="title-popp">${pack.name} - ${pack.version}</h2>

                    <div class="info-details-list">
                        <p><strong>Creator(s):</strong> ${creatorsFormatted}</p>
                        <p><strong>Version:</strong> ${pack.version}</p>
                        <p><strong>Resolution:</strong> ${resolutionDisplay}</p> <p style="font-size: 12px; color: #777;">ID: ${pack.id}</p>
                    </div>

                    <button 
                        id="popupDownloadBtn" 
                        class="download-btn"
                        data-url="${pack.download}">
                        Download (${pack.version})
                    </button>
                </div>
            </div>

            <hr>

            <div class="popup-bottom-content">
                <p class="description-block">${pack.description || "Description not provided."}</p>

                <div class="action-links">
                    <button 
                        class="details-btn" 
                        onclick="window.open('pack-detail.html?id=${pack.id}', '_self')">
                        View The Post of ${pack.name} &rarr;
                    </button>
                </div>
            </div>

            <img src="${pack.screenshot}" alt="Screenshot" class="popup-image">

            <button id="closePopup" class="closepopup" aria-label="Close Details Popup">Close</button>
        `;

        const popupDlBtn = popupBox.querySelector("#popupDownloadBtn");
        if (popupDlBtn) {
            popupDlBtn.addEventListener("click", () => initiateDownload(pack.download));
        }

        popup.style.display = "flex";
        document.body.classList.add("no-scroll");

        // Event listener for closing the popup
        document.getElementById("closePopup").addEventListener("click", closePopup);
        popup.addEventListener("click", e => {
            if (e.target === popup) {
                closePopup();
            }
        });
    }

    /**
     * Closes the details popup.
     */
    function closePopup() {
        popup.style.display = "none";
        document.body.classList.remove("no-scroll");
    }

    /**
     * Opens the invite popup.
     */
    function openInvitePopup() {
        const discordInviteLink = document.getElementById('discordInviteLink');
        if (discordInviteLink) {
            discordInviteLink.href = DISCORD_INVITE;
        }
        invitePopup.style.display = 'flex';
        document.body.classList.add('no-scroll');
    }

    /**
     * Closes the invite popup.
     */
    function closeInvitePopup() {
        invitePopup.style.display = 'none';
        document.body.classList.remove('no-scroll');
    }

    // ----------------------------------------------------
    // --- GLOBAL EVENT LISTENERS ---
    // ----------------------------------------------------
    
    // Search and Filter Listeners
    searchInput.addEventListener("input", filterAndSortPacks); 
    searchInput.addEventListener("keypress", (e) => { if(e.key === "Enter") filterAndSortPacks(); });
    filterResolutionSelect.addEventListener("change", filterAndSortPacks);
    filterTypeSelect.addEventListener("change", filterAndSortPacks); 
    filterFeaturedSelect.addEventListener("change", filterAndSortPacks); 

    // Add Pack Button Listeners
    if (addPackBtn) {
        addPackBtn.addEventListener('click', openInvitePopup);
    }

    // Invite Popup Close Listeners
    if (inviteCloseBtn) {
        inviteCloseBtn.addEventListener('click', closeInvitePopup);
    }
    invitePopup.addEventListener('click', e => {
        if (e.target === invitePopup) {
            closeInvitePopup();
        }
    });

    // --- INITIALIZATION ---
    fetchPacks();

})();