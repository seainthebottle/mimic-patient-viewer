import pandas as pd
from PySide6.QtWidgets import QWidget, QToolTip
from PySide6.QtCore import Qt, QRect, QPoint, QDateTime
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPalette
from datetime import datetime, time, timedelta

class TreatmentTimelineWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setMouseTracking(True)
        
        self.intervals = []
        self.settings = []
        self.selected_date = None
        
        # 색상 정의
        self.colors = {
            'MV': QColor(0, 120, 215, 200),    # Blue
            'CRRT': QColor(16, 124, 16, 200),  # Green
            'ECMO': QColor(209, 52, 56, 200)   # Red
        }
        
        # ItemID 매핑
        self.item_map = {
            225792: 'MV', 225794: 'MV',
            225802: 'CRRT',
            224660: 'ECMO'
        }
        
        self.setting_labels = {
            223849: 'Mode', 220339: 'PEEP', 223835: 'FiO2', 224685: 'TV', 224690: 'RR',
            227290: 'Mode', 224144: 'Blood Flow', 224153: 'Repl. Rate',
            229270: 'Pump Flow', 229278: 'Sweep', 229280: 'FiO2'
        }

    def set_data(self, intervals, settings, selected_date):
        """
        데이터를 설정하고 화면을 갱신한다.
        intervals: List of (itemid, starttime, endtime)
        settings: List of (itemid, charttime, value, valueuom)
        selected_date: str 'YYYY-MM-DD'
        """
        self.intervals = intervals
        self.settings = settings
        self.selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date() if selected_date else None
        self.update()

    def paintEvent(self, event):
        if not self.selected_date:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # VitalSheetWidget의 subplots_adjust(left=0.1, right=0.95)와 일치시킴
        margin_left = width * 0.1
        margin_right = width * 0.05
        margin_top = 10
        margin_bottom = 30
        
        draw_width = width - margin_left - margin_right
        track_height = (height - margin_top - margin_bottom) // 3
        
        # 배경 및 눈금 그리기 (테마에 맞는 색상 사용)
        text_color = self.palette().color(QPalette.WindowText)
        grid_color = self.palette().color(QPalette.Mid)
        
        painter.setPen(QPen(grid_color, 1, Qt.DashLine))
        for i in range(25):
            x = margin_left + (i * draw_width // 24)
            painter.drawLine(x, margin_top, x, height - margin_bottom)
            if i % 4 == 0:
                painter.setPen(text_color)
                painter.drawText(x - 10, height - 10, f"{i:02d}:00")
                painter.setPen(QPen(grid_color, 1, Qt.DashLine))

        # 트랙 라벨 그리기
        painter.setPen(text_color)
        font = QFont("Arial", 9, QFont.Bold)
        painter.setFont(font)
        tracks = ['MV', 'CRRT', 'ECMO']
        for i, track in enumerate(tracks):
            y = margin_top + i * track_height
            painter.drawText(10, y + track_height // 2 + 5, track)

        # 데이터 그리기
        day_start = datetime.combine(self.selected_date, time.min)
        day_end = datetime.combine(self.selected_date, time.max)
        
        for itemid, start, end in self.intervals:
            track_type = self.item_map.get(itemid)
            if not track_type: continue
            
            track_idx = tracks.index(track_type)
            y = margin_top + track_idx * track_height + 5
            
            # 픽셀 좌표 계산
            start_dt = max(start, day_start)
            end_dt = min(end, day_end)
            
            x_start = margin_left + int((start_dt - day_start).total_seconds() / 86400 * draw_width)
            x_end = margin_left + int((end_dt - day_start).total_seconds() / 86400 * draw_width)
            
            if x_end > x_start:
                rect = QRect(x_start, y, x_end - x_start, track_height - 10)
                painter.setBrush(self.colors[track_type])
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect, 5, 5)

    def mouseMoveEvent(self, event):
        if not self.selected_date: return
        
        x = event.pos().x()
        y = event.pos().y()
        
        width = self.width()
        height = self.height()
        
        # VitalSheetWidget의 subplots_adjust(left=0.1, right=0.95)와 일치시킴
        margin_left = width * 0.1
        margin_right = width * 0.05
        margin_top = 10
        margin_bottom = 30
        draw_width = width - margin_left - margin_right
        track_height = (height - margin_top - margin_bottom) // 3
        
        if x < margin_left or x > width - margin_right:
            QToolTip.hideText()
            return
            
        # 마우스 위치 시간 계산
        total_seconds = (x - margin_left) / draw_width * 86400
        hover_time = datetime.combine(self.selected_date, time.min) + timedelta(seconds=total_seconds)
        
        # 어떤 트랙인지 확인
        tracks = ['MV', 'CRRT', 'ECMO']
        track_idx = (y - margin_top) // track_height
        if 0 <= track_idx < 3:
            track_type = tracks[track_idx]
            
            # 해당 처치가 해당 시간에 활성 상태인지 확인
            active = False
            for itemid, start, end in self.intervals:
                if self.item_map.get(itemid) == track_type and start <= hover_time <= end:
                    active = True
                    break
            
            if active:
                # 셋팅값 찾기 (가장 가까운 시간대)
                relevant_settings = []
                # 해당 트랙의 아이템 아이디들
                valid_ids = [iid for iid, t in self.item_map.items() if t == track_type]
                # 사실 셋팅 아이템 아이디는 별도 리스트임
                setting_ids = [iid for iid, label in self.setting_labels.items() if (track_type == 'MV' and iid in [223849, 220339, 223835, 224685, 224690]) or
                                                                                (track_type == 'CRRT' and iid in [227290, 224144, 224153]) or
                                                                                (track_type == 'ECMO' and iid in [229270, 229278, 229280])]
                
                # hover_time 근처 1시간 이내의 기록을 찾음
                current_settings = {}
                for sid, stime, sval, suom in self.settings:
                    if sid in setting_ids:
                        # 가장 가까운 기록 유지 (단 hover_time 이전 것 우선)
                        if abs((stime - hover_time).total_seconds()) < 3600 * 4: # 4시간 이내 기록
                            label = self.setting_labels[sid]
                            val_str = f"{sval} {suom if suom else ''}".strip()
                            current_settings[label] = val_str
                
                if current_settings:
                    tip_text = f"<b>{track_type} Settings</b> ({hover_time.strftime('%H:%M')})<br/>"
                    tip_text += "<br/>".join([f"{k}: {v}" for k, v in current_settings.items()])
                    QToolTip.showText(event.globalPos(), tip_text, self)
                else:
                    QToolTip.showText(event.globalPos(), f"<b>{track_type}</b> (No settings recorded nearby)", self)
            else:
                QToolTip.hideText()
        else:
            QToolTip.hideText()

    def clear(self):
        self.intervals = []
        self.settings = []
        self.selected_date = None
        self.update()
