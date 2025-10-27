# test_fingerprint_utils.py
# Unit tests for fingerprint utilities

import json
import pytest
import tempfile
import os
from patchright.fingerprint_utils import (
    _normalize_viewport,
    load_fp_json,
    get_context_args,
    random_fp,
    generate_js_overrides,
    DEFAULT_FP
)


class TestNormalizeViewport:
    """Tests for _normalize_viewport function"""
    
    def test_tuple_input(self):
        """Test viewport normalization with tuple input"""
        result = _normalize_viewport((1920, 1080))
        assert result == {"width": 1920, "height": 1080}
        assert isinstance(result["width"], int)
        assert isinstance(result["height"], int)
    
    def test_list_input(self):
        """Test viewport normalization with list input"""
        result = _normalize_viewport([1366, 768])
        assert result == {"width": 1366, "height": 768}
        assert isinstance(result["width"], int)
        assert isinstance(result["height"], int)
    
    def test_dict_input(self):
        """Test viewport normalization with dict input"""
        result = _normalize_viewport({"width": 1280, "height": 800})
        assert result == {"width": 1280, "height": 800}
        assert isinstance(result["width"], int)
        assert isinstance(result["height"], int)
    
    def test_dict_with_string_values(self):
        """Test viewport normalization with dict containing strings"""
        result = _normalize_viewport({"width": "1024", "height": "768"})
        assert result == {"width": 1024, "height": 768}
        assert isinstance(result["width"], int)
        assert isinstance(result["height"], int)
    
    def test_missing_viewport(self):
        """Test viewport normalization with None input"""
        result = _normalize_viewport(None)
        assert "width" in result
        assert "height" in result
        assert isinstance(result["width"], int)
        assert isinstance(result["height"], int)
        assert result["width"] > 0
        assert result["height"] > 0
    
    def test_empty_dict(self):
        """Test viewport normalization with empty dict"""
        result = _normalize_viewport({})
        assert result == {"width": DEFAULT_FP["viewport"]["width"], "height": DEFAULT_FP["viewport"]["height"]}
    
    def test_invalid_tuple(self):
        """Test viewport normalization with invalid tuple"""
        result = _normalize_viewport(("abc", "def"))
        assert "width" in result
        assert "height" in result
        assert isinstance(result["width"], int)
        assert isinstance(result["height"], int)
    
    def test_short_list(self):
        """Test viewport normalization with short list"""
        result = _normalize_viewport([1920])
        assert "width" in result
        assert "height" in result
        # Should fallback to random viewport


class TestLoadFpJson:
    """Tests for load_fp_json function"""
    
    def test_complete_fingerprint(self):
        """Test loading a complete fingerprint JSON"""
        fp_data = {
            "user_agent": "Mozilla/5.0 Test",
            "viewport": {"width": 1920, "height": 1080},
            "timezone": "America/New_York",
            "locale": "en-US",
            "platform": "MacIntel",
            "languages": ["en-US", "en"],
            "device_memory": 16,
            "hardware_concurrency": 12,
            "max_touch_points": 5,
            "color_depth": 24,
            "webdriver": False,
            "device_scale_factor": 2
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(fp_data, f)
            temp_path = f.name
        
        try:
            result = load_fp_json(temp_path)
            assert result["user_agent"] == "Mozilla/5.0 Test"
            assert result["viewport"] == {"width": 1920, "height": 1080}
            assert result["timezone"] == "America/New_York"
            assert result["locale"] == "en-US"
            assert result["platform"] == "MacIntel"
            assert result["languages"] == ["en-US", "en"]
            assert result["device_memory"] == 16
            assert result["hardware_concurrency"] == 12
            assert result["max_touch_points"] == 5
            assert result["color_depth"] == 24
            assert result["webdriver"] is False
            assert result["device_scale_factor"] == 2.0
        finally:
            os.unlink(temp_path)
    
    def test_missing_fields(self):
        """Test loading fingerprint with missing fields"""
        fp_data = {
            "viewport": [1280, 720]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(fp_data, f)
            temp_path = f.name
        
        try:
            result = load_fp_json(temp_path)
            # Should have defaults
            assert result["user_agent"] == DEFAULT_FP["user_agent"]
            assert result["timezone"] == DEFAULT_FP["timezone"]
            assert result["locale"] == DEFAULT_FP["locale"]
            assert result["platform"] == DEFAULT_FP["platform"]
            assert result["languages"] == DEFAULT_FP["languages"]
            assert result["device_memory"] == DEFAULT_FP["device_memory"]
            assert result["hardware_concurrency"] == DEFAULT_FP["hardware_concurrency"]
            assert result["max_touch_points"] == DEFAULT_FP["max_touch_points"]
            assert result["color_depth"] == DEFAULT_FP["color_depth"]
            assert result["webdriver"] == DEFAULT_FP["webdriver"]
        finally:
            os.unlink(temp_path)
    
    def test_malformed_fields(self):
        """Test loading fingerprint with malformed fields"""
        fp_data = {
            "viewport": {"width": "abc", "height": "def"},
            "device_memory": "not_a_number",
            "hardware_concurrency": None,
            "max_touch_points": "xyz",
            "color_depth": [],
            "languages": "en-US"  # String instead of list
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(fp_data, f)
            temp_path = f.name
        
        try:
            result = load_fp_json(temp_path)
            # Should normalize to defaults
            assert result["viewport"] == DEFAULT_FP["viewport"]
            assert result["device_memory"] == DEFAULT_FP["device_memory"]
            assert result["hardware_concurrency"] == DEFAULT_FP["hardware_concurrency"]
            assert result["max_touch_points"] == DEFAULT_FP["max_touch_points"]
            assert result["color_depth"] == DEFAULT_FP["color_depth"]
            assert result["languages"] == ["en-US"]  # Should convert string to list
        finally:
            os.unlink(temp_path)


class TestGetContextArgs:
    """Tests for get_context_args function"""
    
    def test_basic_fingerprint(self):
        """Test get_context_args with basic fingerprint"""
        fp = {
            "user_agent": "Test UA",
            "viewport": {"width": 1920, "height": 1080},
            "timezone": "America/New_York",
            "locale": "en-US",
            "device_scale_factor": 2,
            "color_scheme": "dark"
        }
        
        result = get_context_args(fp)
        
        assert result["user_agent"] == "Test UA"
        assert result["viewport"] == {"width": 1920, "height": 1080}
        assert result["timezone_id"] == "America/New_York"
        assert result["locale"] == "en-US"
        assert result["device_scale_factor"] == 2.0
        assert result["color_scheme"] == "dark"
        assert "proxy" not in result
    
    def test_with_proxy(self):
        """Test get_context_args with proxy"""
        fp = random_fp()
        proxy = "http://proxy.example.com:8080"
        
        result = get_context_args(fp, proxy=proxy)
        
        assert "proxy" in result
        assert result["proxy"] == {"server": proxy}
    
    def test_viewport_normalization(self):
        """Test that viewport is properly normalized"""
        fp = {
            "viewport": [1280, 720]
        }
        
        result = get_context_args(fp)
        
        assert result["viewport"] == {"width": 1280, "height": 720}
        assert isinstance(result["viewport"]["width"], int)
        assert isinstance(result["viewport"]["height"], int)
    
    def test_default_values(self):
        """Test that defaults are applied for missing fields"""
        fp = {}
        
        result = get_context_args(fp)
        
        assert result["user_agent"] == DEFAULT_FP["user_agent"]
        assert result["timezone_id"] == DEFAULT_FP["timezone"]
        assert result["locale"] == DEFAULT_FP["locale"]
        assert result["device_scale_factor"] == 1.0
        assert result["color_scheme"] == "light"
    
    def test_types(self):
        """Test that all return types are correct"""
        fp = random_fp()
        result = get_context_args(fp)
        
        assert isinstance(result["user_agent"], str)
        assert isinstance(result["viewport"], dict)
        assert isinstance(result["viewport"]["width"], int)
        assert isinstance(result["viewport"]["height"], int)
        assert isinstance(result["locale"], str)
        assert isinstance(result["timezone_id"], str)
        assert isinstance(result["device_scale_factor"], float)
        assert isinstance(result["color_scheme"], str)


class TestRandomFp:
    """Tests for random_fp function"""
    
    def test_returns_dict(self):
        """Test that random_fp returns a dictionary"""
        fp = random_fp()
        assert isinstance(fp, dict)
    
    def test_has_required_fields(self):
        """Test that random_fp includes all required fields"""
        fp = random_fp()
        
        required_fields = [
            "user_agent", "viewport", "timezone", "locale",
            "platform", "languages", "device_memory",
            "hardware_concurrency", "max_touch_points",
            "color_depth", "webdriver", "device_scale_factor",
            "color_scheme"
        ]
        
        for field in required_fields:
            assert field in fp, f"Missing field: {field}"
    
    def test_viewport_format(self):
        """Test that viewport is in correct format"""
        fp = random_fp()
        
        assert "width" in fp["viewport"]
        assert "height" in fp["viewport"]
        assert isinstance(fp["viewport"]["width"], int)
        assert isinstance(fp["viewport"]["height"], int)
    
    def test_languages_is_list(self):
        """Test that languages is a list"""
        fp = random_fp()
        assert isinstance(fp["languages"], list)
        assert len(fp["languages"]) > 0
    
    def test_platform_matches_user_agent(self):
        """Test that platform is consistent with user agent"""
        for _ in range(10):  # Test multiple times for randomness
            fp = random_fp()
            ua = fp["user_agent"]
            platform = fp["platform"]
            
            if "Windows" in ua:
                assert platform == "Win32"
            elif "Macintosh" in ua:
                assert platform == "MacIntel"
            elif "iPhone" in ua:
                assert platform == "iPhone"


class TestGenerateJsOverrides:
    """Tests for generate_js_overrides function"""
    
    def test_returns_string(self):
        """Test that generate_js_overrides returns a string"""
        fp = random_fp()
        result = generate_js_overrides(fp)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_contains_key_properties(self):
        """Test that JS code contains key property names"""
        fp = {
            "user_agent": "Test UA",
            "platform": "Win32",
            "languages": ["en-US"],
            "device_memory": 8,
            "hardware_concurrency": 4,
            "max_touch_points": 0,
            "color_depth": 24,
            "webdriver": False,
            "viewport": {"width": 1920, "height": 1080}
        }
        
        result = generate_js_overrides(fp)
        
        # Check for key JavaScript property names in defineProperty calls
        assert "navigator, 'platform'" in result
        assert "navigator, 'languages'" in result
        assert "navigator, 'deviceMemory'" in result
        assert "navigator, 'hardwareConcurrency'" in result
        assert "navigator, 'maxTouchPoints'" in result
        assert "navigator, 'webdriver'" in result
        assert "screen, 'colorDepth'" in result
        assert "screen, 'width'" in result
        assert "screen, 'height'" in result
    
    def test_valid_javascript_structure(self):
        """Test that generated JS has valid structure"""
        fp = random_fp()
        result = generate_js_overrides(fp)
        
        # Check for function structure
        assert "(function()" in result
        assert "})();" in result
        
        # Check for try-catch blocks
        assert "try {" in result
        assert "} catch (e) {}" in result
    
    def test_escapes_special_characters(self):
        """Test that special characters are properly handled"""
        fp = {
            "user_agent": "Test'UA\"with\\special",
            "platform": "Win32",
            "languages": ["en-US"],
            "viewport": {"width": 1920, "height": 1080}
        }
        
        result = generate_js_overrides(fp)
        
        # Should still be a valid string
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_uses_defaults_for_missing_fields(self):
        """Test that defaults are used for missing fields"""
        fp = {}  # Empty fingerprint
        
        result = generate_js_overrides(fp)
        
        # Should still generate valid JS
        assert isinstance(result, str)
        assert len(result) > 0
        assert "navigator, 'platform'" in result
    
    def test_webdriver_false(self):
        """Test that webdriver is set to false"""
        fp = {"webdriver": False}
        result = generate_js_overrides(fp)
        
        assert "false" in result
        assert "navigator, 'webdriver'" in result
    
    def test_webdriver_true(self):
        """Test that webdriver can be set to true"""
        fp = {"webdriver": True}
        result = generate_js_overrides(fp)
        
        assert "true" in result
        assert "navigator, 'webdriver'" in result
    
    def test_languages_json_format(self):
        """Test that languages are properly JSON formatted"""
        fp = {"languages": ["en-US", "en", "de-DE"]}
        result = generate_js_overrides(fp)
        
        # Should contain JSON array representation
        assert '["en-US", "en", "de-DE"]' in result or '["en-US","en","de-DE"]' in result
