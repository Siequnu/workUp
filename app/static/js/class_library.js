$(function() {
	// Define global variable which is updated and accessed by handler function
	var libraryUploadId = 0;
	var apiKey = 'IzOGemUDsaFkkLre8g7ci-26CK3MTNhZfj_sKrfY2xzPKGiZXuFNCA'
	// Handlers
	var showEditFormHandler = function(e) {
		// Get the library upload ID of the clicked item
		libraryUploadId = $(this).parent().closest('div[id]').attr('id');

		// Get library upload data via AJAX
		$.ajax({
			method: "GET",
			url: "/api/v1/library/" + libraryUploadId,
			headers: {'key': apiKey},
			error: function(jqXHR, textStatus, errorThrown) {
				alert('An error occured.');
			},
			success: function(libraryUpload) {
				// Add the data to the edit form div
				$('#edited_upload_title').text(libraryUpload.title);
				$('#edited_upload_description').text(libraryUpload.description);

				var thumbnailFilename = libraryUpload.filename.split('.');
				$("#edited_upload_image").attr("src", "/static/thumbnails/" + thumbnailFilename[0] + ".jpeg");

				$('#formTitleField').val(libraryUpload.title);
				$('#formDescriptionField').val(libraryUpload.description);

			}
		});

		// Don't follow the href
		e.preventDefault();
	};

	var submitEditFormHandler = function(e) {
		// Send data via AJAX
		$.ajax({
			type: "PUT",
			url: "/api/v1/library/" + libraryUploadId,
			contentType: 'application/json',
			headers: {'key': apiKey},
			data: JSON.stringify({
				title: $('#formTitleField').val(),
				description: $('#formDescriptionField').val()
			}),
			error: function(jqXHR, textStatus, errorThrown) {
				alert('An error occured.');
			},
			success: function(libraryUpload) {
				// Hide the modal div
				$('#editFormModal').modal('hide');

				//Update the original library card
				$('#' + libraryUploadId + " #libraryCardTitle").text(libraryUpload.title);
				$('#' + libraryUploadId + " #library_card-description").text(libraryUpload.description);

				toastr.success('Library item ' + libraryUpload.title + ' updated successfully.')

			}
		});

		// Don't POST the form
		e.preventDefault();
	};

	// Events
	$('.editLibraryUpload').click(showEditFormHandler);
	$('#editLibraryUploadForm').submit(submitEditFormHandler);
	$('#modalSaveButton').click(submitEditFormHandler);

});