from zookeepr.lib.base import BaseController
from zookeepr.lib.crud import View
from zookeepr import model
from zookeepr.model import Proposal
from zookeepr.lib.base import *

from pylons import request, response, session, tmpl_context as c

from zookeepr.config.lca_info import file_paths
from datetime import date, datetime
from zookeepr.lib.sort import odict
import os


class ScheduleController(BaseController):
    day_dates = {'monday':    date(2010,1,18),
                 'tuesday':   date(2010,1,19),
                 'wednesday': date(2010,1,20),
                 'thursday':  date(2010,1,21),
                 'friday':    date(2010,1,22),
                 'saturday':  date(2010,1,23)}

    def __before__(self, **kwargs):
        c.get_talk = self._get_talk

    def _get_talk(self, talk_id):
        """ Return a proposal object """
        return Proposal.find_by_id(id=talk_id)

    def view_miniconf(self, id):
        try:
            c.day = request.GET['day']
        except:
            c.day = 'all'
        try:
            c.talk = meta.Session.query(Proposal).filter_by(id=id,accepted=True).one()
        except:
            abort(404)

        return render('/schedule/view_miniconf.myt')

    def view_talk(self, id):
        try:
            c.day = request.GET['day']
        except:
            c.day = 'all'
        try:
            c.talk = meta.Session.query(Proposal).filter_by(id=id,accepted=True).one()
        except:
            abort(404)

        return render('schedule/view_talk.myt')

    def index(self, day):
        if day == None:
            for weekday in self.day_dates:
                if self.day_dates[weekday] == datetime.today().date():
                    c.day = weekday
            if c.day == None:
                c.day = 'monday'
        else:
            c.day = day.lower()

        # get list of slides as dict
        c.slide_list = {}
        if file_paths.has_key('slides_path') and file_paths['slides_path'] != '':
            directory = file_paths['slides_path']
            c.download_path = file_paths['slides_html']
            files = {}
            for filename in os.listdir(directory):
                if os.path.isfile(directory + "/" + filename):
                    files[filename.rsplit('.')[0]] = filename

            c.slide_list = files
            c.download_path = file_paths['slides_html']

        c.ogg_list = {}
        if file_paths.has_key('ogg_path') and file_paths['ogg_path'] != '':
            c.ogg_path = file_paths['ogg_path']
            files = {}
            
        
        c.speex_list = {}
        c.speex_path = 'http://mirror.linux.org.au/2009/speex'

        c.talks = meta.Session.query(Proposal).filter_by(accepted=True)
        if c.day in self.day_dates:
            # this won't work across months as we add a day to get a 24 hour range period and that day can overflow from Jan. (we're fine for 09!)
            c.talks = c.talks.filter(Proposal.scheduled >= self.day_dates[c.day] and Proposal.scheduled < self.day_dates[c.day].replace(day=self.day_dates[c.day].day+1))
        c.programme = odict()
        c.talks.order_by((Proposal.scheduled.asc(), Proposal.finished.desc())).all()
        for talk in c.talks:
            if isinstance(talk.scheduled, date):
                talk_day = talk.scheduled.strftime('%A')
                if c.programme.has_key(talk_day) is not True:
                    c.programme[talk_day] = odict()
                if talk.building is not None:
                    if c.programme[talk_day].has_key(talk.building) is not True:
                        c.programme[talk_day][talk.building] = odict()
                    if c.programme[talk_day][talk.building].has_key(talk.theatre) is not True:
                        c.programme[talk_day][talk.building][talk.theatre] = []
                    c.programme[talk_day][talk.building][talk.theatre].append(talk)
        return render_response('schedule/list.myt')
