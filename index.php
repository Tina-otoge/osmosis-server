<?php
require('_app/main.php');

OSM::$key = $osu_token;

$data   = array();
$player = (array_key_exists('username', $_POST) ? $_POST['username'] : null);
if (!$player && array_key_exists('username', $_GET)) {
	$player = $_GET['username'];
}
$limit  = (array_key_exists('results_limit', $_POST) ? $_POST['results_limit'] : null);
$mode   = (array_key_exists('mode', $_POST) ? $_POST['username'] : 0);
if (!$mode && array_key_exists('mode', $_GET)) {
	$mode = $_GET['mode'];
}

if ($player) {
	foreach (OSM::get_user_recent($player, $mode, $limit) as $play) {
		$row = &$data[$play['beatmap_id']];
		$row = array();

		$row['score'] = OSM::calculate_exscore($play);
		$row['info']  = OSM::get_beatmap($play['beatmap_id']);
		$row['date']  = $play['date'];
	}
}
?>
<html lang="en">

<head>

<title>Osu!mosis - by Tina</title>
<style>
	tr.even {
		background-color: #eee;
	}
	td, th {
		padding: 0.2em;
	}
	th {
		border-bottom: 1px solid #dedede;
	}
	.good-score .exscore {
		color: green;
		font-size: 1.2em;
	}
</style>

</head>

<body>

<form method="post" action=".">
	<div id="name-prompt">
	<label for="username">username: <input type="text" id="username" name="username" value="<?= $player ?>"></label>
	</div>
	<div id="results-prompt">
		<label for="results-limit">Number of results: <input type="range" id="results-limit" name="results_limit" min="1" max="50"></label>
	</div>
	<div id="mode">
		<label for="mode">Mode: <select id="mode" name="mode">
			<option value="0" <?= ($mode == "0" ? 'selected="selected"' : '') ?>>osu!</option>
			<option value="1" <?= ($mode == "1" ? 'selected="selected"' : '') ?>>osu!taiko</option>
			<option value="2" <?= ($mode == "2" ? 'selected="selected"' : '') ?>>osu!catch</option>
			<option value="3" <?= ($mode == "3" ? 'selected="selected"' : '') ?>>osu!mania</option>
		</select></label>
	</div>
	<div id="submit">
		<input type="submit">
	</div>
</form>

<table>
	<thead>
		<tr>
			<th>Date</th>
			<th>Song</th>
			<th>Mapper</th>
			<th>Difficulty</th>
			<th>EX Score</th>
			<th>P.GREATs</th>
			<th>GREATs</th>
			<th>GOODs</th>
			<th>BADs</th>
			<th>Combo</th>
		</tr>
	</thead>
	<tbody>
	<?php foreach (array_values($data) as $line => $row): ?>
		<?php $max_exscore = (int)$row['info']['max_combo'] * 2; $percent_exscore = ($row['score']['exscore'] / $max_exscore) * 100; ?>
		<tr class="<?= ($line % 2 ? 'even' : 'odd') ?> <?= ($percent_exscore >= 90 ? 'good-score' : '') ?>">
			<td><?= $row['date'] ?></td>
			<td><?= sprintf('%s - %s', $row['info']['artist'], $row['info']['title']) ?></td>
			<td><?= $row['info']['creator'] ?></td>
			<td><?= $row['info']['version'] ?></td>
			<td><?= sprintf('<strong class="exscore">%s</strong> / %s (%.0f%%)', $row['score']['exscore'], $max_exscore, $percent_exscore) ?></td>
			<td><?= $row['score']['pgreat'] ?></td>
			<td><?= $row['score']['great'] ?></td>
			<td><?= $row['score']['good'] ?></td>
			<td><?= $row['score']['bad'] ?></td>
			<td><?= sprintf('<strong class="combo">%s</strong> / %s', $row['score']['combo'], $row['info']['max_combo']) ?></td>
		</tr>
	<?php endforeach; ?>
	</tbody>
<table>

</body>
</html>
