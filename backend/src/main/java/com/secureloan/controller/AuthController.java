package com.secureloan.controller;

import com.secureloan.auth.AuthService;
import com.secureloan.dto.LoginResponse;
import com.secureloan.dto.OtpRequest;
import com.secureloan.dto.OtpVerifyRequest;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@CrossOrigin(origins = "*")
public class AuthController {
    private final AuthService authService;
    public AuthController(AuthService authService) { this.authService = authService; }
    @PostMapping("/request-otp")
    public ResponseEntity<?> requestOtp(@Valid @RequestBody OtpRequest request) {
        authService.sendOtp(request.mobileNumber());
        return ResponseEntity.ok(Map.of("success", true, "message", "OTP generated"));
    }
    @PostMapping("/verify-otp")
    public ResponseEntity<LoginResponse> verifyOtp(@Valid @RequestBody OtpVerifyRequest request) {
        return ResponseEntity.ok(authService.verifyLogin(request));
    }
}
