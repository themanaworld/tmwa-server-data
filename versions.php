<?php
$versions = file('versions.txt');
$verinfo = array();
foreach($versions as $ver) {
	if ($verinfo[$ver] != null) {
		$verinfo[$ver]++;
	} else {
		$verinfo[$ver] = 1;
	}
}
arsort($verinfo);
$total = count($versions);
echo '<table border="1px" cellspacing="0px"><tr><th>Client</th><th>No.</th><th>%</th></tr>';
foreach($verinfo as $vi=>$vc) {
	echo '<tr><td>' . $vi . '</td><td>' . $vc . '</td><td>' . round((100/$total)*$vc,2) . '</td></tr>';
}
echo '</table><br />Total number of connections: ' . $total . '<br />Number of different clients reported: '
	. count($verinfo) . '<br /><br />Data retrieved: ' . date('D M d y, g:i a T', filemtime('versions.txt'));
?>