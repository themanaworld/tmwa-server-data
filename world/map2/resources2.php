<?php
header("Content-type: text/plain");
header("Cache-Control: no-store, no-cache, must-revalidate"); 
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");

print file_get_contents ("resources2.txt");
?>
