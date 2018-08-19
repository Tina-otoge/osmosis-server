<?php

class OSM
{

	public static $key = null;

	public static function mods_to_literal($bits) {
		$mod_literals = ['NF', 'EZ', 'Touch', 'HD', 'HR',
			'SD', 'DT', 'RX', 'HT', 'NC', 'FL', 'Auto',
			'SpunOut', 'AP', 'PF', '4K', '5K', '6K', '7K',
			'8K', 'Sudden', 'Random', 'Cinema', 'Target',
			'9K', 'Key Coop', '1K', '3K', '2K', 'v2'];
		$chosen_mods = array();
		$i = 0;
		$bits = (int)$bits;
		foreach ($mod_literals as $mod_literal) {
			if ($bits & pow(2, $i)) {
				$chosen_mods[] = $mod_literal;
			}
			$i += 1;
		}
		return (implode(', ', $chosen_mods));
	}

	public static function calculate_exscore($play) {
		$result = [
			'pgreat' => (int)$play['count300'] + (int)$play['countgeki'],
			'great'  => (int)$play['count100'] + (int)$play['countkatu'],
			'good'   => (int)$play['count50'],
			'bad'    => (int)$play['countmiss'],
			'combo'  => (int)$play['maxcombo'],
		];

		$result['exscore'] = ($result['pgreat'] * 2) + $result['great'];
		return ($result);
	}

	public static function get_user_recent($id, $mode=null, $limit=null) {
		$data = [
			'u'     => $id,
			'm'     => $mode,
			'limit' => $limit,
		];

		return (self::request('get_user_recent', $data));
	}

	public static function get_beatmap($id) {
		$data = [
			'b' => $id,
		];

		$result = self::request('get_beatmaps', $data);

		if (!$result) {
			return (null);
		}
		return ($result[0]);
	}

	private static function request($path, $data, $method='GET')
	{
		$url = sprintf('https://osu.ppy.sh/api/%s?k=%s', $path, self::$key);

		foreach ($data as $key => $value) {
			if ($value !== null) {
				$url .= sprintf('&%s=%s', $key, urlencode($value));
			}
		}

		$result = file_get_contents($url, false);

		if (!$result) {
			return (array());
		}
		return (json_decode($result, true));
	}
}
