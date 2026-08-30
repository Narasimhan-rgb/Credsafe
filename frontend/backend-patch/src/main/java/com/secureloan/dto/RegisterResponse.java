package com.secureloan.dto;

public record RegisterResponse(Long userId, Long beneficiaryId, String beneficiaryCode, String fullName, String mobileNumber, String role, String state, String district, String message) {}
