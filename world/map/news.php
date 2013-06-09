<?php

// configuration variables
$min_version = '0.5.1';
$min_manaplus = '1.1.2.20';
$cur_version = '0.6.1';

// utility functions
function failure_headers()
{
    header('HTTP/1.0 403 Upgrade your client');
    common_headers();
}

function common_headers()
{
    header('Content-type: text/plain');
    header('Cache-Control: no-store, no-cache, must-revalidate');
    header('Cache-Control: post-check=0, pre-check=0', false);
    header('Pragma: no-cache');
}

function starts_with($haystack, $needle)
{
    // avoid allocation
    return strpos($haystack, $needle, 0) === 0;
}

function record_version($agent)
{
    $file = 'versions/' . date('Y-m-d') . '.txt';
    // is touching this really needed?
    touch($file);
    file_put_contents($file, '[' . date('H:i') . "] $agent\n", FILE_APPEND);
}

// response functions
function handle_tmw($agent)
{
    failure_headers();
    echo "##1 The client you're using is really old!\n",
         "##1 Please upgrade to a Mana or ManaPlus client.\n",
         "##1     TMW Staff\n \n";
}

function handle_mana($agent, $min_version)
{
    $version_pos = 5;
    $version_end = strpos($agent, ' ');
    $agent_version = substr($agent, $version_pos, $version_end - $version_pos);
    if (version_compare($agent_version, $min_version) < 0)
    {
        failure_headers();
        echo "##1 The client you're using is no longer\n".
             "##1 supported! Please upgrade to $min_version or\n".
             "##1 higher, or use ManaPlus!\n \n".
             "##1     TMW Staff\n \n";
    }
    else
    {
        common_headers();
    }
}

function handle_manaplus($agent, $min_version)
{
    $version_pos = strpos($agent, '4144 v') + 6;
    $version_end = strpos($agent, ')', $version_pos);
    $agent_version = substr($agent, $version_pos, $version_end - $version_pos);
    if (version_compare($agent_version, $min_version) < 0)
    {
        failure_headers();
        echo "##1 The client you're using is no longer\n",
             "##1 supported! Please upgrade to $min_version or\n",
             "##1 higher!\n \n",
             "##1     TMW Staff\n \n";
    }
    else
    {
        common_headers();
    }
}

function handle_other($agent)
{
    common_headers();
    echo "##1 I have no clue what client you're using. Good luck!\n";
}

function handle_browser($agent)
{
    common_headers();
    echo "##1 It looks like this is a web browser, not a game client\n";
}

// main body
$agent = $_SERVER['HTTP_USER_AGENT'];

if (starts_with($agent, 'TMW'))
{
    handle_tmw($agent);
    record_version($agent);
}
else if (starts_with($agent, 'Mana'))
{
    if (starts_with($agent, 'ManaPlus'))
    {
        handle_manaplus($agent, $min_manaplus);
    }
    else if (starts_with($agent, 'Mana/'))
    {
        handle_mana($agent, $min_version);
    }
    else
    {
        handle_other($agent);
    }
    record_version($agent);
}
else
{
    handle_browser($agent);
}

echo "##9 Latest client version: ##6$cur_version\n \n";
echo "##7 TMW Staff will never ask you for your password.\n";
echo "##7 Anyone doing so is trying to scam you.\n \n";

print file_get_contents('news.txt');
?>
