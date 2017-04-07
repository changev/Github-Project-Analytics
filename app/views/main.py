from flask import Flask,render_template, make_response, request, session, redirect, flash, Blueprint
from flask_script import Manager
from flask_bootstrap import Bootstrap
from datetime import datetime, timedelta
import json
import base64
from calendar import monthrange
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from app.models.organization import Organization
from app.models.team import Team
from app.models.user import User

from app import rackhd_config

main = Blueprint('main', __name__)

def tool_time_range_preprocessing(startDate, endDate):
    if type(startDate) == type(""):
        startDate = datetime.strptime(startDate, "%Y-%m")
    if type(endDate) == type(""):
        endDate = datetime.strptime(endDate, "%Y-%m")
        days_of_month = monthrange(endDate.year, endDate.month)[1]
        endDate = endDate + timedelta(days_of_month, 0)
    print(startDate, endDate)
    return (startDate, endDate)

@main.route("/index.html", methods=['GET'])
@main.route("/index", methods=['GET'])
@main.route("/", methods=['GET'])
def index():
	return render_template('index.html')

@main.route("/global_info", methods=['GET'] )
def global_info(): 
    return render_template('global_info.html')
	
@main.route("/get_global_image", methods=['POST'] )
def get_global_image():
    startDate = request.form['StartDate'] or '2015-10'
    endDate = request.form['EndDate'] or datetime.now()
    startDate, endDate = tool_time_range_preprocessing(startDate, endDate)

    image_name = request.form['image_name']
    
    org = Organization()
    operator = {'prCountsHead': org.draw_pr_count_monthly(startDate, endDate),
                'externalPrCountsHead': org.draw_external_pr_count_monthly(startDate, endDate),
                'reviewCommentsHead': org.draw_comments_monthly(startDate, endDate)}
    image_output = operator[image_name]
    image = base64.b64encode(image_output).decode('UTF-8')
    return make_response(image)  

@main.route("/team_info", methods=['GET'])
def team_info():
    team_name = 'Maglev Team'
    teams = [k for k in rackhd_config.Teams.keys()]
    return render_template('team_info.html', teamName = team_name, teams=teams)

@main.route("/get_team_image", methods=['POST'])
def get_team_image():
    teams = rackhd_config.Teams
    repo = rackhd_config.repos    

    startDate = request.form['StartDate'] or '2015-10'
    endDate = request.form['EndDate'] or datetime.now()
    startDate, endDate = tool_time_range_preprocessing(startDate, endDate)
    image_name = request.form['image_name']

    team_name = request.form['TeamName'] or 'Maglev Team'
    team_members = teams[team_name]

    t = Team(team_name, team_members)
    operator = {'teamPrCountsHead': t.draw_team_pr_count_monthly(startDate, endDate),
                'teamReviewCommentsHead': t.draw_team_comments_count_monthly(startDate, endDate),
                'teamPRAvgDurationHead': t.draw_team_avg_duration_monthly(startDate, endDate),
                'memberPRCountsHead': t.draw_pr_count_member(startDate, endDate),
                'memberReviewCommentsHead': t.draw_comments_count_member(startDate, endDate),
                'memberPRAvgDurationHead': t.draw_avg_duration_member(startDate, endDate)}
    image_output = operator[image_name]
    image = base64.b64encode(image_output).decode('UTF-8')
    return make_response(image)

@main.route("/personal_info", methods=['GET'])
def personal_info(): 
    teams_users = rackhd_config.Teams
    return render_template('personal_info.html', teams_users = teams_users)

@main.route("/get_user_info", methods=['POST'])
def get_user_info():
    teams = rackhd_config.Teams
    repo = rackhd_config.repos
    teamName = request.form['TeamName']
    user = request.form['UserName']

    startDate = request.form['StartDate']
    endDate = request.form['EndDate']	    
    startDate = request.form['StartDate'] or '2015-10'
    endDate = request.form['EndDate'] or datetime.now()
    startDate, endDate = tool_time_range_preprocessing(startDate, endDate)

    team_members = teams[teamName]
    u = User(user, teamName)
    user_data = {}
    user_data['pr_rank'] = u.get_pr_rank(startDate, endDate)
    user_data['comments_rank'] = u.get_comments_rank(startDate, endDate)
    user_data['three_top_review_to'] = u.get_three_top_review_to(startDate, endDate)
    user_data['three_top_review_from'] = u.get_three_top_review_from(startDate, endDate)
    # to be replaced by db
    user_data['avatar_url'] = u.get_avatar_url(rackhd_config.headers)
    return make_response(json.dumps(user_data))
