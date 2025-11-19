"""
Database for tracking uploads and analytics
"""
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
import logging
import json

import config

logger = logging.getLogger(__name__)


class Database:
    """SQLite database for tracking agent activity"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self._ensure_directory()
        self._create_tables()
    
    def _ensure_directory(self):
        """Ensure database directory exists"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Trends table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    keywords TEXT,
                    score INTEGER,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used BOOLEAN DEFAULT 0
                )
            ''')
            
            # Videos table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trend_id INTEGER,
                    script TEXT NOT NULL,
                    metadata TEXT,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (trend_id) REFERENCES trends (id)
                )
            ''')
            
            # Uploads table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS uploads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id INTEGER NOT NULL,
                    platform TEXT NOT NULL,
                    content_id TEXT,
                    url TEXT,
                    status TEXT DEFAULT 'pending',
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (video_id) REFERENCES videos (id)
                )
            ''')
            
            # Analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    upload_id INTEGER NOT NULL,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    comments INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    revenue REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (upload_id) REFERENCES uploads (id)
                )
            ''')
            
            conn.commit()
            logger.info("Database tables created/verified")
    
    def save_trend(self, trend: Dict) -> int:
        """Save a detected trend"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trends (source, title, keywords, score)
                VALUES (?, ?, ?, ?)
            ''', (
                trend['source'],
                trend['title'],
                json.dumps(trend.get('keywords', [])),
                trend.get('score', 0)
            ))
            conn.commit()
            return cursor.lastrowid
    
    def mark_trend_used(self, trend_id: int):
        """Mark a trend as used"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE trends SET used = 1 WHERE id = ?', (trend_id,))
            conn.commit()
    
    def get_unused_trends(self, limit: int = 10) -> List[Dict]:
        """Get trends that haven't been used yet"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM trends
                WHERE used = 0
                ORDER BY score DESC, detected_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def save_video(self, video: Dict, trend_id: int = None) -> int:
        """Save video metadata"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO videos (trend_id, script, metadata, file_path)
                VALUES (?, ?, ?, ?)
            ''', (
                trend_id,
                video['script'],
                json.dumps(video.get('metadata', {})),
                video.get('file_path')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def save_upload(self, video_id: int, platform: str, result: Dict) -> int:
        """Save upload result"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO uploads (video_id, platform, content_id, url, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                video_id,
                platform,
                result.get('content_id'),
                result.get('url'),
                'success' if result.get('url') else 'failed'
            ))
            conn.commit()
            return cursor.lastrowid
    
    def update_analytics(self, upload_id: int, stats: Dict):
        """Update or insert analytics for an upload"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if analytics exist
            cursor.execute('SELECT id FROM analytics WHERE upload_id = ?', (upload_id,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE analytics
                    SET views = ?, likes = ?, comments = ?, shares = ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE upload_id = ?
                ''', (
                    stats.get('views', 0),
                    stats.get('likes', 0),
                    stats.get('comments', 0),
                    stats.get('shares', 0),
                    upload_id
                ))
            else:
                cursor.execute('''
                    INSERT INTO analytics (upload_id, views, likes, comments, shares)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    upload_id,
                    stats.get('views', 0),
                    stats.get('likes', 0),
                    stats.get('comments', 0),
                    stats.get('shares', 0)
                ))
            
            conn.commit()
    
    def get_total_analytics(self) -> Dict:
        """Get aggregate analytics across all platforms"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(comments) as total_comments,
                    SUM(shares) as total_shares,
                    COUNT(DISTINCT upload_id) as total_uploads
                FROM analytics
            ''')
            
            row = cursor.fetchone()
            return {
                'total_views': row[0] or 0,
                'total_likes': row[1] or 0,
                'total_comments': row[2] or 0,
                'total_shares': row[3] or 0,
                'total_uploads': row[4] or 0
            }
    
    def get_platform_performance(self) -> List[Dict]:
        """Get performance metrics by platform"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    u.platform,
                    COUNT(u.id) as uploads,
                    SUM(a.views) as total_views,
                    SUM(a.likes) as total_likes,
                    AVG(a.views) as avg_views
                FROM uploads u
                LEFT JOIN analytics a ON u.id = a.upload_id
                WHERE u.status = 'success'
                GROUP BY u.platform
                ORDER BY total_views DESC
            ''')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_recent_uploads(self, limit: int = 20) -> List[Dict]:
        """Get recent uploads with stats"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    u.id, u.platform, u.url, u.uploaded_at,
                    v.script, v.metadata,
                    a.views, a.likes, a.comments
                FROM uploads u
                JOIN videos v ON u.video_id = v.id
                LEFT JOIN analytics a ON u.id = a.upload_id
                ORDER BY u.uploaded_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
