var pusher = new Pusher('a3d90d6c0e5cfca9fd70', {
	  cluster: 'ap3',
	  forceTLS: true
	});

	var channel = pusher.subscribe('attendance');
	channel.bind('my-event', function(data) {
	  alert(JSON.stringify(data));
	});
	
	
channel.bind('new-record', (data) => {

       $('#attendance').append(`
            <tr>
                <td> <h5>${data.data.username} </h5></td>
            </tr>
       `)
    });