# Copyright (c) 2016, Philippe Proulx <eepp.ca>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of pytoutv nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Philippe Proulx BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from toutv3 import model
import datetime as DT


class _Factory:
    def __init__(self, agent):
        self._agent = agent

    def create_bookmark(self, key, api_obj):
        dt = DT.datetime.strptime(api_obj['Timestamp'][:-4], '%Y%m%d%H%M%S')
        obj = model.Bookmark(self._agent, key=key, creation_date=dt)

        return obj

    def create_user_infos(self, rc_api_obj, toutv_api_obj):
        bookmarks = []

        if 'ProfileItems' in toutv_api_obj:
            for key, api_profile_item in toutv_api_obj['ProfileItems'].items():
                if api_profile_item['IsBookmarked']:
                    bookmark = self.create_bookmark(model.Key(self._agent, key),
                                                    api_profile_item)
                    bookmarks.append(bookmark)

        stats_metas = toutv_api_obj['StatsMetas']
        cls = model.UserInfos
        obj = cls(self._agent, ban_level=rc_api_obj['ban_level'],
                  name=rc_api_obj['name'], email=rc_api_obj['email'],
                  is_hd=toutv_api_obj['IsHD'],
                  bookmarks=bookmarks, stats_metas=stats_metas,
                  rc_telco=stats_metas['rc.telco'],
                  rc_features=stats_metas['rc.forfait'],
                  is_premium=toutv_api_obj['IsPremium'],
                  show_ads=toutv_api_obj['ShowAds'])

        return obj

    def create_section_summary(self, api_obj):
        return model.SectionSummary(self._agent, name=api_obj['Name'],
                                    title=api_obj['Title'])

    def create_search_show_summary(self, api_obj):
        cls = model.SearchShowSummary
        obj = cls(self._agent, is_free=api_obj['IsFree'],
                  image_url=api_obj['ImageUrl'],
                  searchable_text=api_obj['SearchableText'],
                  key=model.Key(self._agent, api_obj['Key']),
                  url=api_obj['Url'],
                  is_media=api_obj['IsMedia'],
                  is_geolocalized=api_obj['IsGeolocalized'],
                  title=api_obj['DisplayText'])

        return obj

    def create_show_lineup_item(self, api_obj):
        if api_obj['Share'] is None or api_obj['Url'] is None:
            return

        api_key = api_obj['Key']
        key = api_key

        if api_key is None:
            key = api_obj['BookmarkKey']

        cls = model.ShowLineupItem
        obj = cls(self._agent, key=model.Key(self._agent, key),
                  description=api_obj['Description'],
                  image_url=api_obj['ImageUrl'], is_active=api_obj['IsActive'],
                  is_drm=api_obj['IsDrm'], is_free=api_obj['IsFree'],
                  is_geolocalized=api_obj['IsGeolocalized'],
                  length_text=api_obj['Length'],
                  share_url=api_obj['Share']['Url'],
                  template=api_obj['Template'], title=api_obj['Title'],
                  url=api_obj['Url'])

        return obj

    def create_subsection_lineup(self, api_obj):
        api_lineup_items = api_obj['LineupItems']
        items = []

        if type(api_lineup_items) is list:
            for api_lineup_item in api_lineup_items:
                item = self.create_show_lineup_item(api_lineup_item)

                if item is not None:
                    items.append(item)

        cls = model.SubsectionLineup
        obj = cls(self._agent, name=api_obj['Name'], title=api_obj['Title'],
                  is_free=api_obj['IsFree'], items=items)

        return obj

    def create_section(self, api_obj):
        api_lineups = api_obj['Lineups']
        subsection_lineups = []

        if type(api_lineups) is list:
            for api_lineup in api_lineups:
                subsection_lineups.append(self.create_subsection_lineup(api_lineup))

        cls = model.Section
        obj = cls(self._agent, name=api_obj['Name'], title=api_obj['Title'],
                  subsection_lineups=subsection_lineups,
                  stats_metas=api_obj['StatsMetas'])

        return obj

    def create_network(self, api_obj):
        return model.Network(self._agent, name=api_obj['Name'],
                             image_url=api_obj['ImageUrl'], url=api_obj['Url'],
                             title=api_obj['Title'])

    def create_credits(self, api_obj):
        return model.Credits(self._agent, role=api_obj['Key'],
                             names=api_obj['Value'])

    def create_details(self, api_obj):
        credits = []
        networks = []
        length = None
        api_persons = api_obj['Persons']
        api_networks = api_obj['Networks']
        api_length = api_obj['Length']

        if type(api_persons) is list:
            for api_person in api_persons:
                credits.append(self.create_credits(api_person))

        if type(api_networks) is list:
            for api_network in api_networks:
                networks.append(self.create_network(api_network))

        if type(api_length) is int:
            length = DT.timedelta(seconds=api_length)

        cls = model.Details
        obj = cls(self._agent, rating=api_obj['Rating'],
                  air_date_text=api_obj['AirDate'],
                  original_title=api_obj['OriginalTitle'], credits=credits,
                  copyright=api_obj['Copyright'], country=api_obj['Country'],
                  description=api_obj['Description'],
                  production_year=api_obj['ProductionYear'],
                  length_text=api_obj['LengthText'], length=length,
                  details_type=api_obj['Type'], image_url=api_obj['ImageUrl'],
                  networks=networks)

        return obj

    def create_show(self, api_obj):
        api_season_lineups = api_obj['SeasonLineups']
        season_lineups = []

        if type(api_season_lineups) is list:
            for api_season_lineup in api_season_lineups:
                season_lineups.append(self.create_season_lineup(api_season_lineup))

        if api_obj['Details2']:
            details = self.create_details(api_obj['Details2'])
        elif api_obj['Details']:
            details = self.create_details(api_obj['Details'])
        else:
            details = None

        cls = model.Show
        obj = cls(self._agent, key=model.Key(self._agent, api_obj['Key']),
                  description=api_obj['Description'],
                  bg_image_url=api_obj['BackgroundImageUrl'],
                  image_url=api_obj['ImageUrl'], title=api_obj['Title'],
                  details=details, season_lineups=season_lineups,
                  stats_metas=api_obj['StatsMetas'])

        return obj

    def create_season_lineup(self, api_obj):
        api_lineup_items = api_obj['LineupItems']
        items = []

        if type(api_lineup_items) is list:
            for api_lineup_item in api_lineup_items:
                items.append(self.create_episode_lineup_item(api_lineup_item))

        cls = model.SeasonLineup
        obj = cls(self._agent, name=api_obj['Name'], title=api_obj['Title'],
                  url=api_obj['Url'], is_free=api_obj['IsFree'],
                  items=items)

        return obj

    def create_episode_lineup_item(self, api_obj):
        details = self.create_details(api_obj['Details'])
        cls = model.EpisodeLineupItem
        obj = cls(self._agent, template=api_obj['Template'],
                  is_active=api_obj['IsActive'], url=api_obj['Url'],
                  is_free=api_obj['IsFree'],
                  key=model.Key(self._agent, api_obj['Key']),
                  is_geolocalized=api_obj['IsGeolocalized'],
                  image_url=api_obj['ImageUrl'], title=api_obj['Title'],
                  is_drm=api_obj['IsDrm'], description=api_obj['Description'],
                  share_url=api_obj['Share']['AbsoluteUrl'], details=details)

        return obj