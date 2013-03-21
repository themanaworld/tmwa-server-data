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

$min_version = '0.5.0';
$cur_version = '0.6.1';

if (substr($agent, 0, 3) == "TMW")
{
    echo "##1 The client you're using is really old!\n",
         "##1 Please upgrade to a Mana or ManaPlus client.\n",
         "##1     TMW Staff\n \n";
}

if (substr($agent, 0, 5) == "Mana/"
    and $agent < 'Mana/' . $min_version)
{
    echo "##1 The client you're using is no longer\n".
         "##1 supported! Please upgrade to $min_version or\n".
         "##1 higher, or use ManaPlus!\n \n".
         "##1     TMW Staff\n \n";
}

echo "##9 Latest client version: ##6$cur_version\n \n";
echo "##7 TMW Staff will never ask you for your password.\n";
echo "##7 Anyone doing so is trying to scam you.\n \n";

print file_get_contents("news.txt");
?>
