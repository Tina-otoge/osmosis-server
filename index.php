<?php
require('_app/main.php');

OSM::$key = $osu_token;

$data   = array();
$player = (array_key_exists('username', $_GET) ? $_GET['username'] : null);
$limit  = (array_key_exists('results_limit', $_GET) ? $_GET['results_limit'] : null);
$mode   = (array_key_exists('mode', $_GET) ? $_GET['username'] : 0);

if ($player) {
	foreach (OSM::get_user_recent($player, $mode, $limit) as $key => $play) {
		$data[$key] = [
			'date'       => $play['date'],
			'mods'       => $play['enabled_mods'],
			'score'      => OSM::calculate_exscore($play),
			'info'       => OSM::get_beatmap($play['beatmap_id']),
		];
		$data[$key]['info']['mods_string'] = OSM::mods_to_literal((int)($play['enabled_mods']));
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

<script>
function alternateTable() {
	var table = document.getElementById('results');
	var visible_row = 0;

	for (var i = 0; row = table.rows[i]; i += 1) {
		if (row.style.display != 'none') {
			visible_row += 1;
		}
		if (visible_row % 2) {
			row.classList.remove('odd');
			row.classList.add('even');
		} else {
			row.classList.add('odd');
			row.classList.remove('even');
		}
	}
}

function showBest() {
	var table = document.getElementById('results');
	var scores = {};
	var index = null;

	for (var i = 0; row = table.rows[i]; i += 1) {
		index = row.dataset.beatmap + '-' + row.dataset.mods;	
		if (!(index in scores)) {
			scores[index] = row;
		} else {
			if (parseInt(row.dataset.exscore, 10) > parseInt(scores[index].dataset.exscore, 10)) {
				scores[index].style.display = "none";
				scores[index] = row;
			} else {
				row.style.display = "none";
			}
		}
	}
	alternateTable();
}

function showAll() {
	var table = document.getElementById('results');

	for (var i = 0; row = table.rows[i]; i += 1) {
		row.style.display = "table-row";
	}
	alternateTable();
}

function takeHidedupAction() {
	var checkbox = document.getElementById('hide-dup');

	if (checkbox.checked) {
		showBest();
	} else {
		showAll();
	}
}

function hidedupHandler() {
	takeHidedupAction();
};
</script>

</head>

<body onload="takeHidedupAction();">

<form method="get" action=".">
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

<div id="hidedup-prompt">
	<label for="hide-dup"><abbr title="hide retries">Only show best</abbr> <input type="checkbox" name="hide-dup" id="hide-dup" checked="checked" onchange="hidedupHandler();"></label>
</div>
<table id="results">
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
	<?php foreach ($data as $row): ?>
		<?php $max_exscore = (int)$row['info']['max_combo'] * 2; $percent_exscore = ($row['score']['exscore'] / $max_exscore) * 100; ?>
		<tr
		data-beatmap="<?= $row['info']['beatmap_id'] ?>"
		data-mods="<?= $row['mods'] ?>"
		data-exscore="<?= $row['score']['exscore'] ?>"
		<?= ($percent_exscore >= 90 ? 'class="good-score"' : '') ?>>
			<td><?= $row['date'] ?></td>
			<td><a href="https://osu.ppy.sh/beatmapsets/<?= $row['info']['beatmapset_id'] ?>"> <?= sprintf('%s - %s', $row['info']['artist'], $row['info']['title']) ?></a></td>
			<td><a href="https://osu.ppy.sh/users/<?= $row['info']['creator_id'] ?>"><?= $row['info']['creator'] ?></a></td>
			<td><a href="https://osu.ppy.sh/b/<?= $row['info']['beatmap_id'] ?>"><?= $row['info']['version'] ?></a> (<?= sprintf('%.2f', $row['info']['difficultyrating']) ?>&star;) <?= $row['info']['mods_string'] ?></td>
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
