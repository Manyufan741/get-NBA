
// async function processForm(evt) {
//     evt.preventDefault();
//     const $player_first_name = $('#first_name').val();
//     const $player_last_name = $('#last_name').val();
//     console.log("player full name", $player_first_name, "++", $player_last_name);
//     const response = await axios.post('http://127.0.0.1:5000/api/get-player-stats', json = { "player_first_name": $player_first_name, "player_last_name": $player_last_name });
//     handleResponse(response);
// }

// function handleResponse(resp) {
//     $results = $('#search-results');
//     $results.empty();
//     console.log("response", resp);
//     if (resp.data) {
//         result_amount = resp.data.length;
//         console.log("length", result_amount);
//         for (let i = 0; i < result_amount; i++) {
//             first_name = resp.data[i].first_name;
//             last_name = resp.data[i].last_name;
//             team = resp.data[i].team;
//             $player = $(`<p>${first_name} ${last_name} is currently with team ${team}.</p>`);
//             $results.append($player);
//         }
//     } else {
//         $results.append($('<p>Player not found.</p>'));
//     }
// }

// $("#player-search-form").on("submit", processForm);