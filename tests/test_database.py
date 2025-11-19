"""Tests for Database"""
import pytest
import os
import json
from datetime import datetime

from src.database import Database


class TestDatabase:
    
    @pytest.fixture
    def db(self, mock_database):
        """Create test database instance"""
        return Database(db_path=mock_database)
    
    def test_initialization(self, db):
        """Test database initialization"""
        assert db is not None
        assert os.path.exists(db.db_path)
    
    def test_tables_created(self, db):
        """Test all tables are created"""
        import sqlite3
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'trends' in tables
            assert 'videos' in tables
            assert 'uploads' in tables
            assert 'analytics' in tables
    
    def test_save_trend(self, db, sample_trend):
        """Test saving a trend"""
        trend_id = db.save_trend(sample_trend)
        
        assert isinstance(trend_id, int)
        assert trend_id > 0
    
    def test_mark_trend_used(self, db, sample_trend):
        """Test marking trend as used"""
        trend_id = db.save_trend(sample_trend)
        db.mark_trend_used(trend_id)
        
        unused = db.get_unused_trends()
        assert not any(t['id'] == trend_id for t in unused)
    
    def test_get_unused_trends(self, db, sample_trend):
        """Test fetching unused trends"""
        # Save multiple trends
        db.save_trend(sample_trend)
        db.save_trend(sample_trend)
        
        unused = db.get_unused_trends(limit=10)
        
        assert isinstance(unused, list)
        assert len(unused) == 2
        assert all(t['used'] == 0 for t in unused)
    
    def test_save_video(self, db, sample_script, sample_metadata):
        """Test saving video metadata"""
        video_data = {
            'script': sample_script,
            'metadata': sample_metadata,
            'file_path': '/path/to/video.mp4'
        }
        
        video_id = db.save_video(video_data, trend_id=1)
        
        assert isinstance(video_id, int)
        assert video_id > 0
    
    def test_save_upload(self, db, sample_script, sample_metadata):
        """Test saving upload result"""
        video_data = {
            'script': sample_script,
            'metadata': sample_metadata,
            'file_path': '/path/to/video.mp4'
        }
        video_id = db.save_video(video_data)
        
        upload_result = {
            'url': 'https://youtube.com/shorts/test123',
            'content_id': 'test123'
        }
        
        upload_id = db.save_upload(video_id, 'youtube', upload_result)
        
        assert isinstance(upload_id, int)
        assert upload_id > 0
    
    def test_update_analytics_new(self, db, sample_script, sample_metadata):
        """Test creating new analytics entry"""
        video_data = {
            'script': sample_script,
            'metadata': sample_metadata,
            'file_path': '/path/to/video.mp4'
        }
        video_id = db.save_video(video_data)
        upload_id = db.save_upload(video_id, 'youtube', {'url': 'test'})
        
        stats = {
            'views': 1000,
            'likes': 50,
            'comments': 10,
            'shares': 5
        }
        
        db.update_analytics(upload_id, stats)
        
        # Verify analytics were saved
        total_stats = db.get_total_analytics()
        assert total_stats['total_views'] == 1000
        assert total_stats['total_likes'] == 50
    
    def test_update_analytics_existing(self, db, sample_script, sample_metadata):
        """Test updating existing analytics"""
        video_data = {
            'script': sample_script,
            'metadata': sample_metadata,
            'file_path': '/path/to/video.mp4'
        }
        video_id = db.save_video(video_data)
        upload_id = db.save_upload(video_id, 'youtube', {'url': 'test'})
        
        # Initial analytics
        db.update_analytics(upload_id, {'views': 100, 'likes': 5})
        
        # Update
        db.update_analytics(upload_id, {'views': 200, 'likes': 10})
        
        total_stats = db.get_total_analytics()
        assert total_stats['total_views'] == 200
        assert total_stats['total_likes'] == 10
    
    def test_get_total_analytics_empty(self, db):
        """Test total analytics with no data"""
        stats = db.get_total_analytics()
        
        assert stats['total_views'] == 0
        assert stats['total_likes'] == 0
        assert stats['total_uploads'] == 0
    
    def test_get_total_analytics_with_data(self, db, sample_script, sample_metadata):
        """Test total analytics aggregation"""
        # Create multiple uploads with analytics
        video_data = {
            'script': sample_script,
            'metadata': sample_metadata,
            'file_path': '/path/to/video.mp4'
        }
        
        for i in range(3):
            video_id = db.save_video(video_data)
            upload_id = db.save_upload(video_id, 'youtube', {'url': f'test{i}'})
            db.update_analytics(upload_id, {
                'views': 100 * (i + 1),
                'likes': 10 * (i + 1),
                'comments': i + 1
            })
        
        stats = db.get_total_analytics()
        
        assert stats['total_views'] == 600  # 100 + 200 + 300
        assert stats['total_likes'] == 60   # 10 + 20 + 30
        assert stats['total_comments'] == 6  # 1 + 2 + 3
    
    def test_get_platform_performance(self, db, sample_script, sample_metadata):
        """Test platform performance metrics"""
        video_data = {
            'script': sample_script,
            'metadata': sample_metadata,
            'file_path': '/path/to/video.mp4'
        }
        
        # Add uploads for different platforms
        video_id = db.save_video(video_data)
        
        youtube_id = db.save_upload(video_id, 'youtube', {'url': 'yt_test'})
        tiktok_id = db.save_upload(video_id, 'tiktok', {'url': 'tt_test'})
        
        db.update_analytics(youtube_id, {'views': 1000, 'likes': 50})
        db.update_analytics(tiktok_id, {'views': 2000, 'likes': 100})
        
        performance = db.get_platform_performance()
        
        assert isinstance(performance, list)
        assert len(performance) == 2
        
        # Should be sorted by total_views DESC
        assert performance[0]['platform'] == 'tiktok'
        assert performance[0]['total_views'] == 2000
    
    def test_get_recent_uploads(self, db, sample_script, sample_metadata):
        """Test fetching recent uploads"""
        video_data = {
            'script': sample_script,
            'metadata': sample_metadata,
            'file_path': '/path/to/video.mp4'
        }
        
        for i in range(5):
            video_id = db.save_video(video_data)
            db.save_upload(video_id, 'youtube', {'url': f'test{i}'})
        
        recent = db.get_recent_uploads(limit=3)
        
        assert isinstance(recent, list)
        assert len(recent) == 3
        assert all('platform' in r for r in recent)
        assert all('url' in r for r in recent)
