from flask import render_template, flash, current_app, request, redirect, url_for, send_from_directory
from flask_login import current_user, login_required

import datetime

from app.models import Assignment, Enrollment, ClassLibraryFile, Assignment, StatementProject, Inquiry, Feedback
import app.assignments.models
import app.files.models
from app import db
from app.main import bp
import app.user

# Elm video
import pathlib
import subprocess
import os.path
import json

# Statements
try:
    import app.consultations.models
except:
    pass

# Goals
try:
    import app.goals.models
except:
    pass

# Mentors
try:
    import app.mentors.models
except:
    pass


@current_app.before_request
def before_request():
    if current_user.is_authenticated:
        if app.files.models.new_library_files_since_last_seen():
            flash('New library files have been uploaded!', 'info')
        current_user.last_seen = datetime.datetime.now()
        db.session.commit()

@current_app.after_request
def close_request_session(response):
    # 解决mysql server gone away
    db.session.remove()
    return response

# Main entrance to the app


@bp.route('/')
@bp.route('/index')
def index():
    # Dynamically generate the index template name based on app name
    index_template = str('index_') + current_app.config['APP_NAME'] + '.html'

    if current_user.is_authenticated:
        # All models get the greeting
        greeting = app.main.models.get_greeting()

        # For admin views
        if app.models.is_admin(current_user.username):
            return render_template(
                index_template, admin=True,
                greeting=greeting,

                # Lessons today
                lessons_today = app.classes.models.get_teacher_lessons_today_from_teacher_id (current_user.id),

                # Student count and info
                active_user_count=app.user.models.get_active_user_count(),
                student_count=app.user.models.get_total_user_count(),
                classes=app.assignments.models.get_all_class_info(),

                # Library
                library=ClassLibraryFile.query.all(),
                total_library_downloads=app.files.models.get_total_library_downloads_count(),
                total_library_count = ClassLibraryFile.query.count(),

                # Assignments
                assignments=Assignment.query.all(),
                total_uploads = app.files.models.get_all_uploads_count(),

                # Statements
                statement_projects=StatementProject.query.all(
                ) if app.models.custom_service_is_enabled('statements') else False,
                statement_projects_needing_review=app.statements.models.get_projects_needing_review(
                ) if app.models.custom_service_is_enabled('statements') else False,

            )
        # Student views
        else:
            # Display help message if a student has signed up and is not part of a class
            if Enrollment.query.filter(Enrollment.user_id == current_user.id).first() is None:
                flash(
                    'You do not appear to be part of a class. Please contact your tutor for assistance.', 'warning')
                return render_template(index_template)
            return render_template(
                index_template,

                # Assignments
                assignments_info=app.assignments.models.get_user_assignment_info(
                    current_user.id),
                number_of_uploads=app.files.models.get_uploaded_file_count_from_user_id(
                    current_user.id),
                upload_progress_percentage=app.assignments.models.get_assignment_upload_progress_bar_percentage(
                    current_user.id),
                last_upload_humanized_timestamp=app.assignments.models.last_uploaded_assignment_timestamp(
                    current_user.id),

                # Peer reviews
                peer_review_progress_percentage=app.assignments.models.get_peer_review_progress_bar_percentage(
                    current_user.id),
                total_completed_peer_reviews=app.assignments.models.get_total_completed_peer_reviews(
                    current_user.id),
                number_of_peer_reviews_on_own_uploads=app.assignments.models.get_received_peer_review_count(
                    current_user.id),
                received_peer_review_count=app.assignments.models.get_received_peer_review_count(
                    current_user.id),
                last_received_peer_review_humanized_timestamp=app.assignments.models.last_incoming_peer_review_timestamp(
                    current_user.id),

                # Library
                library_file_count=len(
                    app.files.models.get_user_library_books_from_id(current_user.id)),
                library_download_stat=app.files.models.get_total_downloads_for_user(
                    current_user.id),

                # Attendance
                attendance_stats_percentage=app.classes.models.get_user_attendance_record_stats(
                    current_user.id, percentage=True),
                attendance_stats=app.classes.models.get_user_attendance_record_stats(
                    current_user.id),

                # Greeting
                greeting=greeting,

                # Consultations
                consultations=app.consultations.models.get_consultation_info_array(
                    current_user.id) if app.models.custom_service_is_enabled('consultations') else False,

                # Goals
                goals=app.goals.models.get_student_goals_from_user_id(
                        current_user.id) if app.models.custom_service_is_enabled('goals') else False,

                # Mentors
                mentors=app.mentors.models.get_mentors_from_student_id(
                        current_user.id) if app.models.custom_service_is_enabled('mentors') else False
            )

    # If user is not authenticated, redirect to these product pages
    if current_app.config['APP_NAME'] == 'workUp':
        return render_template('workUp/product.html')
    elif current_app.config['APP_NAME'] == 'elmOnline':
        return render_template('elmOnline/elm_product.html')
    elif current_app.config['APP_NAME'] == 'LCECAcademy':
        return render_template('lcec/lcec_product.html')
    else:
        return render_template(index_template)


@bp.route('/superintendant')
def superintendant ():
    if current_user.is_authenticated and app.models.is_admin(current_user.username) and current_user.is_superintendant:
        return render_template(
            'superintendant.html',

            # Student count and info
            active_user_count=app.user.models.get_active_user_count(),
            student_count=app.user.models.get_total_user_count(),
            classes=app.assignments.models.get_all_class_info(),

            # Library
            library=ClassLibraryFile.query.all(),
            total_library_downloads=app.files.models.get_total_library_downloads_count(),
            total_library_count = ClassLibraryFile.query.count(),

            # Assignments
            assignments=Assignment.query.all(),
            total_uploads = app.files.models.get_all_uploads_count(),

            # Statements
            statement_projects=StatementProject.query.all(
            ) if app.models.custom_service_is_enabled('statements') else False,
            statement_projects_needing_review=app.statements.models.get_projects_needing_review(
            ) if app.models.custom_service_is_enabled('statements') else False,

            # Sign-up codes
            sign_up_code = current_app.config['SIGNUP_CODES']

        )
    return redirect (url_for ('main.index'))


@bp.route('/superintendant/stats')
def superintendant_stats ():
    if current_user.is_authenticated and app.models.is_admin(current_user.username) and current_user.is_superintendant:
        return render_template(
            'superintendant_stats.html',

            # Student count and info
            active_user_count=app.user.models.get_active_user_count(),
            student_count=app.user.models.get_total_user_count(),
            classes=app.assignments.models.get_all_class_info(),

            # Library
            library=ClassLibraryFile.query.all(),
            total_library_downloads=app.files.models.get_total_library_downloads_count(),
            total_library_count = ClassLibraryFile.query.count(),

            # Assignments
            assignments=Assignment.query.all(),
            total_uploads = app.files.models.get_all_uploads_count(),

            # Statements
            statement_projects=StatementProject.query.all(
            ) if app.models.custom_service_is_enabled('statements') else False,
            statement_projects_needing_review=app.statements.models.get_projects_needing_review(
            ) if app.models.custom_service_is_enabled('statements') else False,

        )
    return redirect (url_for ('main.index'))




#
#
#                                                                             kkkkkkkk          UUUUUUUU     UUUUUUUU
#                                                                             k::::::k          U::::::U     U::::::U
#                                                                             k::::::k          U::::::U     U::::::U
#                                                                             k::::::k          UU:::::U     U:::::UU
#  wwwwwww           wwwww           wwwwwww ooooooooooo   rrrrr   rrrrrrrrr   k:::::k    kkkkkkkU:::::U     U:::::Uppppp   ppppppppp
#   w:::::w         w:::::w         w:::::woo:::::::::::oo r::::rrr:::::::::r  k:::::k   k:::::k U:::::D     D:::::Up::::ppp:::::::::p
#    w:::::w       w:::::::w       w:::::wo:::::::::::::::or:::::::::::::::::r k:::::k  k:::::k  U:::::D     D:::::Up:::::::::::::::::p
#     w:::::w     w:::::::::w     w:::::w o:::::ooooo:::::orr::::::rrrrr::::::rk:::::k k:::::k   U:::::D     D:::::Upp::::::ppppp::::::p
#      w:::::w   w:::::w:::::w   w:::::w  o::::o     o::::o r:::::r     r:::::rk::::::k:::::k    U:::::D     D:::::U p:::::p     p:::::p
#       w:::::w w:::::w w:::::w w:::::w   o::::o     o::::o r:::::r     rrrrrrrk:::::::::::k     U:::::D     D:::::U p:::::p     p:::::p
#        w:::::w:::::w   w:::::w:::::w    o::::o     o::::o r:::::r            k:::::::::::k     U:::::D     D:::::U p:::::p     p:::::p
#         w:::::::::w     w:::::::::w     o::::o     o::::o r:::::r            k::::::k:::::k    U::::::U   U::::::U p:::::p    p::::::p
#          w:::::::w       w:::::::w      o:::::ooooo:::::o r:::::r           k::::::k k:::::k   U:::::::UUU:::::::U p:::::ppppp:::::::p
#           w:::::w         w:::::w       o:::::::::::::::o r:::::r           k::::::k  k:::::k   UU:::::::::::::UU  p::::::::::::::::p
#            w:::w           w:::w         oo:::::::::::oo  r:::::r           k::::::k   k:::::k    UU:::::::::UU    p::::::::::::::pp
#             www             www            ooooooooooo    rrrrrrr           kkkkkkkk    kkkkkkk     UUUUUUUUU      p::::::pppppppp
#                                                                                                                    p:::::p
#                                                                                                                    p:::::p
#                                                                                                                   p:::::::p
#                                                                                                                   p:::::::p
#                                                                                                                   p:::::::p
#                                                                                                                   ppppppppp
#

# workUp specific routing

# Redirect for lesson registration
@bp.route('/attend')
def lesson_registration_redirect():
    return redirect(url_for('classes.enter_attendance_code'))

# Features of the website
@bp.route('/product')
def product():
    if current_app.config['APP_NAME'] == 'workUp':
        return render_template('workUp/product.html')
    else:
        return redirect(url_for('main.index'))


# Features of the website
@bp.route('/brochure')
def brochure():
    if current_app.config['APP_NAME'] == 'workUp':
        return send_from_directory(filename='WorkUp brochure public.pdf',
                                   directory='static/',
                                   as_attachment = True,
                                   attachment_filename = 'WorkUp - Learning Management Software.pdf')
    else:
        return redirect(url_for('main.index'))

@bp.route('/teachers')
def product_teachers():
    if current_app.config['APP_NAME'] == 'workUp':
        return render_template('workUp/teachers.html')
    else:
        return redirect(url_for('main.index'))

@bp.route('/consultancies')
def product_consultancies():
    if current_app.config['APP_NAME'] == 'workUp':
        return render_template('workUp/consultancies.html')
    else:
        return redirect(url_for('main.index'))

# URL for UK contract purposes
@bp.route('/features')
def features():
    return redirect(url_for('main.index'))

# URL for THU feedback
@bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if current_app.config['APP_NAME'] == 'workUp':
        if request.method == 'POST':
            feedback = Feedback(
                loved=request.form.get('loved'),
                improve=request.form.get('improve'),
                learn=request.form.get('learn'),
                valuable=request.form.get('valuable'),
                timestamp=datetime.datetime.now()
            )
            feedback.save()
            # ¡# Send email to to admin?
            flash(
                'Thank you for your feedback. See you soon!', 'success')
            return redirect(url_for('main.product'))
        else:
            return render_template('workUp/feedback.html')
    else:
        return redirect(url_for('main.index'))

# Inquiry form
@bp.route('/feedback/view')
@login_required
def view_feedback():
    if current_app.config['APP_NAME'] == 'workUp':
        if app.models.is_admin(current_user.username):
            feedbacks = Feedback.query.all()
            return render_template('workUp/view_feedback.html', feedbacks=feedbacks)
    return redirect(url_for('main.index'))

# Inquiry form
@bp.route('/feedback/delete/<feedback_id>')
@login_required
def delete_feedback(feedback_id):
    if current_app.config['APP_NAME'] == 'workUp':
        if app.models.is_admin(current_user.username):
            feedback = Feedback.query.get(feedback_id)
            feedback.delete()
            flash('Removed the feedback.', 'success')
            return redirect(url_for('main.view_feedback'))
    else:
        return redirect(url_for('main.index'))


@bp.route('/inquire', methods=['GET', 'POST'])
def inquire():
    if current_app.config['APP_NAME'] == 'workUp':
        if request.method == 'POST':
            inquiry = Inquiry(
                name=request.form.get('name'),
                email=request.form.get('email-address'),
                message=request.form.get('message'),
                timestamp=datetime.datetime.now()
            )
            inquiry.save()
            # ¡# Send email to to admin?
            flash(
                'Thank you! We have received your enquiry and will be in touch soon.', 'success')
            return redirect(url_for('main.product'))
        else:
            return render_template('workUp/inquire.html')
    else:
        return redirect(url_for('main.index'))

# Inquiry form
@bp.route('/inquiries/view', methods=['GET', 'POST'])
@login_required
def view_inquiries():
    if current_app.config['APP_NAME'] == 'workUp':
        if app.models.is_admin(current_user.username) and current_user.is_superintendant:
            inquiries = Inquiry.query.all()
            return render_template('workUp/view_inquiries.html', inquiries=inquiries)
    return redirect(url_for('main.index'))

# Inquiry form
@bp.route('/inquiries/delete/<inquiry_id>')
@login_required
def delete_inquiry(inquiry_id):
    if current_app.config['APP_NAME'] == 'workUp':
        if app.models.is_admin(current_user.username) and current_user.is_superintendant:
            inquiry = Inquiry.query.get(inquiry_id)
            inquiry.delete()
            flash('Removed the inquiry.', 'success')
            return redirect(url_for('main.view_inquiries'))
    else:
        return redirect(url_for('main.index'))


@bp.route('/inquiries/delete/all/')
@login_required
def delete_all_inquiries():
    """
    Deletes all inquiries
    """
    if current_app.config['APP_NAME'] == 'workUp':
        if app.models.is_admin(current_user.username) and current_user.is_superintendant:
            inquiries = Inquiry.query.all()
            for inquiry in inquiries:
                db.session.delete(inquiry)
            db.session.commit()
            flash('Deleted all inquiries.', 'success')
            return redirect(url_for('main.view_inquiries'))
    else:
        return redirect(url_for('main.index'))


#             /$$                /$$$$$$            /$$ /$$
#            | $$               /$$__  $$          | $$|__/
#    /$$$$$$ | $$ /$$$$$$/$$$$ | $$  \ $$ /$$$$$$$ | $$ /$$ /$$$$$$$   /$$$$$$
#   /$$__  $$| $$| $$_  $$_  $$| $$  | $$| $$__  $$| $$| $$| $$__  $$ /$$__  $$
#  | $$$$$$$$| $$| $$ \ $$ \ $$| $$  | $$| $$  \ $$| $$| $$| $$  \ $$| $$$$$$$$
#  | $$_____/| $$| $$ | $$ | $$| $$  | $$| $$  | $$| $$| $$| $$  | $$| $$_____/
#  |  $$$$$$$| $$| $$ | $$ | $$|  $$$$$$/| $$  | $$| $$| $$| $$  | $$|  $$$$$$$
#   \_______/|__/|__/ |__/ |__/ \______/ |__/  |__/|__/|__/|__/  |__/ \_______/
#
#
#
# elmOnline specific routing
# Page that displays the QR code
@bp.route('/contact')
def contact():
    if current_app.config['APP_NAME'] == 'elmOnline':
        return render_template('elmOnline/contact.html')
    else:
        return redirect(url_for('main.index'))

@bp.route('/admissions')
def elm_admissions():
    if current_app.config['APP_NAME'] == 'elmOnline': return render_template('elmOnline/elm_admissions.html')
    else: return redirect(url_for('main.index'))

@bp.route('/team')
def elm_team():
    if current_app.config['APP_NAME'] == 'elmOnline': return render_template('elmOnline/elm_team.html')
    else: return redirect(url_for('main.index'))

@bp.route('/elm/inquire', methods=['GET', 'POST'])
def elm_inquire():
    if current_app.config['APP_NAME'] == 'elmOnline':
        if request.method == 'POST':
            inquiry = Inquiry(
                name=request.form.get('name'),
                email=request.form.get('email-address'),
                message=request.form.get('message'),
                timestamp=datetime.datetime.now()
            )
            inquiry.save()
            # ¡# Send email to to admin?
            flash(
                'Thank you! We have received your enquiry and will be in touch soon.', 'success')
            return redirect(url_for('main.index'))
        else:
            return render_template('elmOnline/elm_inquire.html')
    else:
        return redirect(url_for('main.index'))

@bp.route('/videos', methods=['GET', 'POST'])
def elm_videos():
    if current_app.config['APP_NAME'] == 'elmOnline':
        # Calculate the path to the videos
        path_to_workup = pathlib.Path().absolute()
        path_to_videos = str(path_to_workup) + '/app/static/elm/videos/'

        # Dictionary of videos
        videos_file = open('app/static/elm/videos/videos.json')
        videos = json.load(videos_file)

        # Generate thumbnails if necessary for any of the videos
        for video in videos:
            video_input_path = path_to_videos + video['filename'] + video['extension']
            img_output_path = path_to_videos + video['filename'] + '.jpg'

            # If thumbnail missing, generate it
            if os.path.isfile (img_output_path) is False:
                subprocess.call(['ffmpeg', '-i', video_input_path, '-ss', '00:00:10.000', '-vframes', '1', img_output_path])

        # Video categories
        categories_file = open('app/static/elm/videos/categories.json')
        categories = json.load(categories_file)

        return render_template('elmOnline/elm_videos.html', videos = videos, categories = categories)
    else:
        return redirect(url_for('main.index'))