package com.secureloan.controller;

import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.secureloan.auth.RegistrationService;
import com.secureloan.dto.RegisterRequest;
import com.secureloan.dto.RegisterResponse;

@RestController
@RequestMapping("/api/auth")
public class RegistrationController {
    private final RegistrationService registrationService;
    public RegistrationController(RegistrationService registrationService){this.registrationService=registrationService;}
    @PostMapping("/register")
    public RegisterResponse register(@RequestBody RegisterRequest request){return registrationService.register(request);}
    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<ErrorBody> invalid(IllegalArgumentException e){return ResponseEntity.badRequest().body(new ErrorBody(e.getMessage()));}
    @ExceptionHandler(DuplicateKeyException.class)
    public ResponseEntity<ErrorBody> duplicate(DuplicateKeyException e){return ResponseEntity.status(HttpStatus.CONFLICT).body(new ErrorBody(e.getMessage()));}
    public record ErrorBody(String message){}
}
