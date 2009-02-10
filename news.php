<?php
header("Content-type: text/plain");
header("Cache-Control: no-store, no-cache, must-revalidate");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");

$agent = $_SERVER['HTTP_USER_AGENT'];

if (substr($agent, 0, 3) == "TMW")
{
  file_put_contents('versions.txt', "$agent\n", FILE_APPEND);
}

if ($agent == "TMW/0.0.23")
{
  echo "##1 The client you're using is no longer\n".
       "##1 supported! Please upgrade to 0.0.25 or\n".
       "##1 higher!\n \n";
}
else if ($agent == "TMW/0.0.24" ||
         $agent == "TMW/0.0.24.1")
{
  echo "##1 On Monday, November 3rd, support for your\n".
       "##1 client version will be dropped. Please\n".
       "##1 upgrade to 0.0.25 or later!\n \n TMW Staff\n \n";
}

print file_get_contents ("news.txt");
?>
