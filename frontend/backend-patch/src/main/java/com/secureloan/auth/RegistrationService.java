package com.secureloan.auth;

import org.springframework.dao.DuplicateKeyException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import com.secureloan.dto.RegisterRequest;
import com.secureloan.dto.RegisterResponse;

@Service
public class RegistrationService {
    private final JdbcTemplate jdbcTemplate;
    public RegistrationService(JdbcTemplate jdbcTemplate){this.jdbcTemplate=jdbcTemplate;}

    @Transactional
    public RegisterResponse register(RegisterRequest request){
        String fullName=clean(request.fullName());
        String mobile=clean(request.mobileNumber());
        String state=clean(request.state());
        String district=clean(request.district());
        String email=nullable(request.email());
        String address=nullable(request.address());
        if(fullName==null||fullName.isBlank()) throw new IllegalArgumentException("Full name is required");
        if(mobile==null||!mobile.matches("\\d{10}")) throw new IllegalArgumentException("A valid 10-digit mobile number is required");
        if(district==null||district.isBlank()) throw new IllegalArgumentException("District is required");
        if(state==null||state.isBlank()) state="Tamil Nadu";
        Integer existing=jdbcTemplate.queryForObject("select count(*) from users where mobile_number = ?",Integer.class,mobile);
        if(existing!=null&&existing>0) throw new DuplicateKeyException("An account already exists for this mobile number");
        Long userId=jdbcTemplate.queryForObject("""
            insert into users (full_name,mobile_number,email,role,enabled,created_at)
            values (?, ?, ?, 'BENEFICIARY', true, current_timestamp) returning id
            """,Long.class,fullName,mobile,email);
        String beneficiaryCode=String.format("BEN-%05d",userId);
        Long beneficiaryId=jdbcTemplate.queryForObject("""
            insert into beneficiaries (user_id,beneficiary_code,state,district,address,identity_verified)
            values (?, ?, ?, ?, ?, false) returning id
            """,Long.class,userId,beneficiaryCode,state,district,address);
        return new RegisterResponse(userId,beneficiaryId,beneficiaryCode,fullName,mobile,"BENEFICIARY",state,district,"Account created successfully. Request OTP to sign in.");
    }
    private String clean(String v){return v==null?null:v.trim();}
    private String nullable(String v){String x=clean(v);return x==null||x.isBlank()?null:x;}
}
