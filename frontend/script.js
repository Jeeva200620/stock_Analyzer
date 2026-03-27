document.addEventListener('DOMContentLoaded', () => {


    const csvUpload = document.getElementById('csv-upload');
    const weekdaySelect = document.getElementById('weekday');
    const analyzeBtn = document.getElementById('analyze-btn');
    const resultsSection = document.getElementById('results');
    const loadingSection = document.getElementById('loading');
    const tableBody = document.getElementById('table-body');

    let allData = []; // Store parsed CSV data

    csvUpload.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                try {
                    allData = parseCSV(event.target.result);
                    alert("CSV loaded successfully! Please click Analyze Data.");
                } catch (error) {
                    console.error("Error parsing CSV:", error);
                    alert("Failed to parse CSV file. Ensure it contains Date, Open, High, Low, Close columns.");
                }
            };
            reader.readAsText(file);
        }
    });

    analyzeBtn.addEventListener('click', () => {
        performAnalysis();
    });

    weekdaySelect.addEventListener('change', () => {
        if (allData.length > 0 && resultsSection.style.display !== 'none') {
            performAnalysis();
        }
    });

    function parseCSV(text) {
        const lines = text.trim().split('\n');
        if (lines.length < 2) return [];

        const headerLine = lines[0].toLowerCase().replace(/"/g, '');
        const headers = headerLine.split(',').map(h => h.trim());
        
        const getIdx = (keywords, defaultIdx) => {
            let idx = headers.findIndex(h => keywords.some(k => h.includes(k)));
            return idx !== -1 ? idx : defaultIdx;
        };

        let dateIdx = getIdx(['date', ' d ', 'time'], 0);
        let openIdx = getIdx(['open'], 1);
        let highIdx = getIdx(['high'], 2);
        let lowIdx = getIdx(['low'], 3);
        let closeIdx = getIdx(['close', 'last', 'ltp'], 4);
        let volumeIdx = getIdx(['volume', 'vol', 'shares', 'qty', 'quantity', 'turnover'], 5);

        let data = [];
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        
        for (let i = 1; i < lines.length; i++) {
            if (!lines[i].trim()) continue;
            
            // Split respecting quotes, then remove quotes AND thousands separator commas
            const parts = lines[i].split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/).map(p => p.trim().replace(/"/g, '').replace(/,/g, ''));
            if (parts.length <= closeIdx && parts.length <= openIdx) continue;
            
            const dateStr = parts[dateIdx];
            let dateObj;
            
            if (dateStr.includes('-')) {
                const p = dateStr.split('-');
                if (p[0].length === 4) { // YYYY-MM-DD
                    dateObj = new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2].substring(0, 2)));
                } else if (p[2].length === 4 || p[2].length === 2) { // DD-MMM-YYYY or DD-MM-YY
                    let year = Number(p[2]);
                    if (year < 100) year += 2000;
                    
                    let m = Number(p[1]);
                    if (isNaN(m)) {
                        m = new Date(`${p[1]} 1, 2000`).getMonth();
                    } else {
                        m = m - 1;
                    }
                    dateObj = new Date(year, m, Number(p[0]));
                } else {
                    dateObj = new Date(dateStr);
                }
            } else if (dateStr.includes('/')) {
                const p = dateStr.split('/');
                let year = Number(p[2]);
                if (year < 100) year += 2000;
                
                if (Number(p[1]) > 12) {
                    // MM = p[0], DD = p[1]
                    dateObj = new Date(year, Number(p[0]) - 1, Number(p[1]));
                } else if (Number(p[0]) > 12) {
                    // DD = p[0], MM = p[1]
                    dateObj = new Date(year, Number(p[1]) - 1, Number(p[0]));
                } else {
                    // Assume DD/MM/YYYY
                    dateObj = new Date(year, Number(p[1]) - 1, Number(p[0]));
                }
            } else {
                dateObj = new Date(dateStr);
            }

            if (!dateObj || isNaN(dateObj.getTime())) continue;

            const openVal = openIdx >= 0 ? parseFloat(parts[openIdx]) : 0;
            const highVal = highIdx >= 0 ? parseFloat(parts[highIdx]) : 0;
            const lowVal = lowIdx >= 0 ? parseFloat(parts[lowIdx]) : 0;
            const closeVal = closeIdx >= 0 ? parseFloat(parts[closeIdx]) : 0;
            const volVal = volumeIdx >= 0 ? parseFloat(parts[volumeIdx]) : 0;

            if (!isNaN(openVal) && !isNaN(closeVal)) {
                const mm = String(dateObj.getMonth() + 1).padStart(2, '0');
                const dd = String(dateObj.getDate()).padStart(2, '0');
                const yy = dateObj.getFullYear();
                
                data.push({
                    date: dateStr,
                    rawDate: dateObj.getTime(),
                    formattedDate: `${yy}-${mm}-${dd}`,
                    weekdayName: days[dateObj.getDay()],
                    open: openVal,
                    high: highVal,
                    low: lowVal,
                    close: closeVal,
                    volume: isNaN(volVal) ? 0 : volVal
                });
            }
        }
        
        // Ensure chronological order unconditionally
        data.sort((a, b) => a.rawDate - b.rawDate);
        for (let i = 0; i < data.length; i++) {
            if (i > 0 && data[i-1].close > 0) {
                // Standard return compared to previous close
                data[i].return_percent = ((data[i].close - data[i-1].close) / data[i-1].close) * 100;
            } else if (data[i].open > 0) {
                data[i].return_percent = ((data[i].close - data[i].open) / data[i].open) * 100;
            } else {
                data[i].return_percent = 0;
            }
        }

        return data;
    }

    function performAnalysis() {
        if (allData.length === 0) {
            alert("Please upload a CSV file first.");
            return;
        }

        const weekday = weekdaySelect.value;
        resultsSection.style.display = 'none';
        loadingSection.style.display = 'block';

        setTimeout(() => {
            try {
                displayStockData(weekday);
                resultsSection.style.display = 'grid';
                setTimeout(() => lucide.createIcons(), 50);
            } catch (error) {
                console.error(error);
                alert("Error analyzing data.");
            } finally {
                loadingSection.style.display = 'none';
            }
        }, 300); // Simulate loading delay for polish
    }

    function displayStockData(targetWeekday) {
        // filter by weekday, e.g., 'Monday', 'Tuesday', etc.
        const filteredData = allData.filter(d => d.weekdayName.includes(targetWeekday));
        
        tableBody.innerHTML = '';
        // Sort newest first using precise local timestamps
        const sortedData = [...filteredData].sort((a, b) => b.rawDate - a.rawDate);

        sortedData.forEach(record => {
            const tr = document.createElement('tr');
            const isPos = record.return_percent > 0;
            const returnClass = isPos ? 'positive' : 'negative';
            
            // Use safely formatted date constructed at parse-time without shifting timezones
            let dateStrFormatted = record.formattedDate;

            tr.innerHTML = `
                <td style="font-weight: 500;">${dateStrFormatted}</td>
                <td style="color: var(--primary);">${record.weekdayName}</td>
                <td>${record.open.toFixed(2)}</td>
                <td>${record.high.toFixed(2)}</td>
                <td>${record.low.toFixed(2)}</td>
                <td>${record.close.toFixed(2)}</td>
                <td style="color: var(--text-muted); font-size: 0.85rem;">${record.volume.toLocaleString()}</td>
                <td class="${returnClass}" style="font-weight: 600;">
                    ${isPos ? '▲' : '▼'} ${Math.abs(record.return_percent).toFixed(2)}%
                </td>
            `;
            tableBody.appendChild(tr);
        });
    }



});
