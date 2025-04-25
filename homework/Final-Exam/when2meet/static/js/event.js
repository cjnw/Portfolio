// Constants
const AVAILABLE_STATUS = 'available';
const MAYBE_STATUS = 'maybe';
const UNAVAILABLE_STATUS = 'unavailable';

// State variables
let currentStatus = AVAILABLE_STATUS;
let isDragging = false;
let myAvailability = new Set(); // Track cells marked by current user
let currentUserId = null; // Store current user ID

// DOM Elements
const eventId = document.getElementById('event-id').value;
const socket = io();

// Event Handlers
const handleConnect = () => {
    console.log('Connected to WebSocket server');
    socket.emit('join_event', { event_id: eventId });
};

const handleDisconnect = () => {
    console.log('Disconnected from WebSocket server');
};

const handleInitialAvailability = (data) => {
    console.log('Received initial availability:', data);
    currentUserId = data.current_user_id;
    
    // Initialize myAvailability with cells marked by current user
    data.availability.forEach(entry => {
        if (entry.user_id === currentUserId) {
            const key = `${entry.date}-${entry.time_slot}`;
            myAvailability.add(key);
            
            // Update the cell's appearance
            const cell = document.querySelector(`[data-date="${entry.date}"][data-time="${entry.time_slot}"]`);
            if (cell) {
                const statusDiv = cell.querySelector('.availability-status');
                const indicator = cell.querySelector('.personal-indicator');
                
                if (statusDiv) {
                    statusDiv.classList.remove(AVAILABLE_STATUS, MAYBE_STATUS, UNAVAILABLE_STATUS);
                    statusDiv.classList.add(entry.status);
                }
                
                if (indicator) {
                    indicator.classList.add('visible');
                }
            }
        }
    });
    
    // Update the grid with all availability data
    updateAvailabilityGrid(data.availability);
    updateBestTime(data.best_time);
};

const handleAvailabilityUpdate = (data) => {
    console.log('Received availability update:', data);
    updateAvailabilityGrid(data.availability, data.current_user_id);
    
    // Update best time display
    const bestTimeElement = document.getElementById('best-time');
    if (data.best_time) {
        bestTimeElement.textContent = `${data.best_time.date} ${data.best_time.time_slot}`;
    } else {
        bestTimeElement.textContent = 'No best time available yet';
    }
};

const handleCellMouseDown = (event) => {
    console.log('handleCellMouseDown called');
    event.preventDefault();
    isDragging = true;
    const cell = event.target.closest('.availability-cell');
    if (cell) {
        console.log('Found cell to update:', cell);
        updateCell(cell);
    }
};

const handleCellMouseOver = (event) => {
    if (isDragging) {
        console.log('handleCellMouseOver called');
        const cell = event.target.closest('.availability-cell');
        if (cell) {
            console.log('Found cell to update:', cell);
            updateCell(cell);
        }
    }
};

const handleCellMouseUp = () => {
    isDragging = false;
};

// Utility Functions
const updateStatus = (status) => {
    console.log('Updating status to:', status);
    currentStatus = status;
    // Remove active class from all buttons
    document.querySelectorAll('.availability-controls .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    // Add active class to selected button
    const selectedBtn = document.querySelector(`.availability-controls .btn[data-status="${status}"]`);
    if (selectedBtn) {
        selectedBtn.classList.add('active');
    }
};

const updateCell = (cell) => {
    console.log('updateCell called with:', cell);
    if (cell && cell.classList.contains('availability-cell')) {
        const date = cell.getAttribute('data-date');
        const time_slot = cell.getAttribute('data-time');
        const cellKey = `${date}-${time_slot}`;
        
        console.log('Updating cell:', { date, time_slot, status: currentStatus });
        
        // Get the status div and indicator
        const statusDiv = cell.querySelector('.availability-status');
        const indicator = cell.querySelector('.personal-indicator');
        
        console.log('Found elements:', { statusDiv, indicator });
        
        // Check if we're trying to make a cell unavailable
        if (currentStatus === UNAVAILABLE_STATUS) {
            // Get the current count of available users
            const currentCount = parseInt(statusDiv.getAttribute('data-count') || '0');
            // Only allow making unavailable if this user is the only one who had availability
            if (currentCount > 1) {
                alert('You cannot make this time unavailable because other users have marked it as available.');
                return;
            }
        }
        
        if (statusDiv) {
            console.log('Current status div classes:', statusDiv.classList);
            // Remove all status classes first
            statusDiv.classList.remove(AVAILABLE_STATUS, MAYBE_STATUS, UNAVAILABLE_STATUS);
            // Force a reflow to ensure class removal is processed
            statusDiv.offsetHeight;
            // Add the new status class
            statusDiv.classList.add(currentStatus);
            // Remove any inline styles that might interfere
            statusDiv.removeAttribute('style');
            console.log('Updated status div classes:', statusDiv.classList);
            console.log('Computed background color:', window.getComputedStyle(statusDiv).backgroundColor);
        }
        
        if (indicator) {
            // Remove all status classes from indicator
            indicator.classList.remove(AVAILABLE_STATUS, MAYBE_STATUS, UNAVAILABLE_STATUS);
            // Add the current status class
            indicator.classList.add(currentStatus);
            indicator.classList.add('visible');
            indicator.removeAttribute('style');
        }
        
        // Track this cell as marked by the current user
        myAvailability.add(cellKey);
        
        // Emit the update to the server
        socket.emit('update_availability', {
            event_id: eventId,
            date: date,
            time_slot: time_slot,
            status: currentStatus
        });
    }
};

const updateAvailabilityGrid = (availability) => {
    // Group availability by cell and count statuses
    const cellAvailability = {};
    availability.forEach(entry => {
        const key = `${entry.date}-${entry.time_slot}`;
        if (!cellAvailability[key]) {
            cellAvailability[key] = { available: 0, maybe: 0, unavailable: 0, total: 0 };
        }
        cellAvailability[key][entry.status]++;
        cellAvailability[key].total++;
    });

    Object.entries(cellAvailability).forEach(([key, counts]) => {
        const [date, time_slot] = key.split('-');
        const cell = document.querySelector(`[data-date="${date}"][data-time="${time_slot}"]`);
        if (cell) {
            const statusDiv = cell.querySelector('.availability-status');
            if (statusDiv) {
                statusDiv.className = 'availability-status';
                statusDiv.removeAttribute('style');
                let dominantStatus = UNAVAILABLE_STATUS;
                let color = '#E0E0E0'; // default: unavailable
                if (counts.available > 0) {
                    dominantStatus = AVAILABLE_STATUS;
                    if (counts.available === 1) color = '#C8E6C9'; // light green
                    else if (counts.available === 2) color = '#81C784'; // medium green
                    else color = '#2E7D32'; // dark green
                } else if (counts.maybe > 0) {
                    dominantStatus = MAYBE_STATUS;
                    color = '#FFC107'; // yellow
                }
                statusDiv.classList.add(dominantStatus);
                statusDiv.style.backgroundColor = color;
                statusDiv.style.opacity = 1; // always fully opaque for clarity
            }
        }
    });
};

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing event listeners');
    
    // Socket event listeners
    socket.on('connect', handleConnect);
    socket.on('disconnect', handleDisconnect);
    socket.on('initial_availability', handleInitialAvailability);
    socket.on('availability_update', handleAvailabilityUpdate);
    
    // Initialize status buttons
    document.querySelectorAll('.availability-controls .btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const status = btn.getAttribute('data-status');
            console.log('Button clicked:', status);
            updateStatus(status);
        });
    });
    
    // Initialize grid cells
    const cells = document.querySelectorAll('.availability-cell');
    console.log('Found cells:', cells.length);
    
    cells.forEach(cell => {
        console.log('Adding listeners to cell:', cell);
        cell.addEventListener('mousedown', handleCellMouseDown);
        cell.addEventListener('mouseover', handleCellMouseOver);
        cell.addEventListener('click', (event) => {
            console.log('Cell clicked:', cell);
            event.preventDefault();
            updateCell(cell);
        });
    });
    
    document.addEventListener('mouseup', handleCellMouseUp);
    
    // Set initial status
    updateStatus(AVAILABLE_STATUS);
});