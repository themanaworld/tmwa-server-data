<?php
$file = 'versions/' . date('Y-m-d') . '.txt';
if (!file_exists($file)) touch($file); // Make sure it exists

$versions = file($file);
$verinfo = array();
foreach($versions as $version) {
    $ver = substr($version, 8); // Ignore time information
    if ($verinfo[$ver] != null) {
        $verinfo[$ver]++;
    } else {
        $verinfo[$ver] = 1;
    }
}

arsort($verinfo);

$total = count($versions);
print '<table border="1px" cellspacing="0px" cellpadding="1px"><tr><th>Client</th><th title="Count">n</th><th title="Percent of total">%</th></tr>';
foreach($verinfo as $vi=>$vc) {
    echo '<tr><td>' . $vi . '</td><td>' . $vc . '</td><td>' . round((100 / $total) * $vc, 2) . '</td></tr>';
}
print '</table><br />Total number of connections: ' . $total . '<br />Number of different clients reported: '
     . count($verinfo) . '<br /><br />Data retrieved: ' . date('D M d y, g:i a T', filemtime($file));
?>