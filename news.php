<?php
header("Content-type: text/plain");
header("Cache-Control: no-store, no-cache, must-revalidate");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");

$agent = $_SERVER['HTTP_USER_AGENT'];

if (substr($agent, 0, 3) == "TMW" || substr($agent, 0, 4) == "Mana")
{
    $file = 'versions/' . date('Y-m-d') . '.txt';
    touch($file);
    file_put_contents($file, '[' . date('H:i') . "] $agent\n", FILE_APPEND);
}

$old_versions = array("TMW/0.0.23", "TMW/0.0.24", "TMW/0.0.24.1", "TMW/0.0.25");
$min_version = '0.0.26';

if (array_search($agent, $old_versions) !== FALSE) // Explicit check for saftey
{
    echo "##1 The client you're using is no longer\n".
         "##1 supported! Please upgrade to $min_version or\n".
         "##1 higher!\n \n".
         "##1     TMW Staff\n \n";
}

print file_get_contents("news.txt");
?>
