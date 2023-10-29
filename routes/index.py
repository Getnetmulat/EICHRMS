
from models.modules import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import plotly
from datetime import date
import plotly.graph_objects as go
import plotly.express as px
## Blueprint Configuration
dashboard_bp = Blueprint(
    'dashboard_bp', __name__,
    template_folder='templates',
    static_folder='static'
)
## Blueprint Configuration
@dashboard_bp.route('/', methods=['GET'])
# route page to index/login
def index():
    collageNames = Collage.query.all()
    try:
        return render_template('login.html', collageNames = collageNames)
    except TemplateNotFound:
        abort(404)
#
@dashboard_bp.route('/dashboard/', methods=['GET'])
@login_required
# route page to index/login
def dashboard():

    bins = [18, 25, 35, 45, 55, 65, 100]
    labels=['18-25', '26-35', '36-45', '46-55', '56-65', '66 >']
    fig, fig2,fig_edu = None, None, None
        # count the number of rows of region
    count = Collage.query.count()
    plan_percent = None
    # Query the leaders data from Leader table
    if current_user.has_role('super-admin') or current_user.has_role('admin'):
        emp_query = db.session.query(Employee).join(Collage).with_entities(Employee.id, Employee.gender, Collage.collageName, Employee.age, Employee.qualification).all()
        df = pd.DataFrame.from_records(emp_query, index='id', columns=['id', 'gender', 'collageID','age','Educational Level'])

        df_age = df.groupby(['collageID', 'gender'])['gender'].count().reset_index(name="count")
        df_edu = df.groupby(['Educational Level', 'gender'])['gender'].count().reset_index(name='count')
        df_age_g = df # copy to
        df_age_g.dropna(inplace=True)# drop rows if NaN value exists
        df_age_g['age_group'] = pd.cut(df_age_g['age'].astype(int), bins=bins, labels=labels) # convert tuple column to string

        age_group_df = df_age_g.groupby(['age_group', 'gender'])['gender'].count().reset_index(name="count")

        fig = px.histogram(df_age, x='collageID', y='count', color='gender', barmode='group',
        title=" Employee Data in Gender", labels={ # replaces default labels by column name
                    "gender": "Gender",  "collageID": "Collages", "count": "gender"})

        fig2 = px.histogram(age_group_df, x='age_group', y='count', hover_data=['gender'], color='gender', barmode='group',
            title="Employee Data in Age", labels={ # replaces default labels by column name
                    "gender": "Gender", "age_group": "Age", "count": "Age Interval" })
        fig_edu = px.histogram(df_edu, x='Educational Level', y='count', hover_data=['gender'], color='gender', barmode='group',
            title="Employee Data in Educational Level", labels={ # replaces default labels by column name
                    "gender": "Gender", "Employee": "Educational Level",  "count": "Employee" })
        
        collage_id = db.session.query(User.collageID).filter(User.id==current_user.id).first() # get Collage ID of the current user
        branch_count = db.session.query(Branch).filter(Branch.collageID==collage_id[0]).count() # count the number of rows of Campus
        
        emp_count = db.session.query(Employee).filter(Employee.collageID==collage_id[0]).count() # count the number of rows of Employee
        dep_count = db.session.query(Department).count() # count the number of rows of Department
        pos_count = db.session.query(Position).count() # count the number of rows of Position
    
    # if request.method == 'GET':
        graph_gender = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        age_group =json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        gender_edu = json.dumps(fig_edu, cls=plotly.utils.PlotlyJSONEncoder)
        
        
    return render_template('dashboard.html',graph_gender =graph_gender, age_group =age_group, gender_edu=gender_edu, collage_count = count, branch_count = branch_count,  emp_count = emp_count, dep_count = dep_count, pos_count = pos_count)

