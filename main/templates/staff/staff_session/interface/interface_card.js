/**
 * take update from client for new location target
 */
// take_target_location_update: function take_target_location_update(message_data)
// {
//     if(message_data.value == "success")
//     {
//         app.session.world_state.session_players[message_data.session_player_id].target_location = message_data.target_location;             
//     } 
//     else
//     {
        
//     }
// },

update_player_inventory: function update_player_inventory()
{

    let period_id = app.session.session_periods_order[app.session.world_state.current_period-1];

    for(const i in app.session.session_players_order)
    {
        const player_id = app.session.session_players_order[i];
        pixi_avatars[player_id].inventory_label = app.session.world_state.session_players[player_id].inventory[period_id];
    }
},
