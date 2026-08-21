package com.secureloan.security;

import com.secureloan.dto.SecurityRiskAssessment;
import com.secureloan.enums.SecuritySeverity;
import org.springframework.stereotype.Service;
import java.util.ArrayList;
import java.util.List;

@Service
public class SecurityCorrelationService {
    private final BehaviourRiskService behaviourRiskService;
    private final IpRiskService ipRiskService;
    private final FamiliarFraudRiskService familiarFraudRiskService;
    private final AccountTakeoverService accountTakeoverService;
    public SecurityCorrelationService(BehaviourRiskService behaviourRiskService, IpRiskService ipRiskService, FamiliarFraudRiskService familiarFraudRiskService, AccountTakeoverService accountTakeoverService) {
        this.behaviourRiskService = behaviourRiskService; this.ipRiskService = ipRiskService; this.familiarFraudRiskService = familiarFraudRiskService; this.accountTakeoverService = accountTakeoverService;
    }
    public SecurityRiskAssessment correlate(Long userId, String ipAddress, Long loanId) {
        var behaviour = behaviourRiskService.analyse(userId);
        var ip = ipRiskService.analyse(ipAddress);
        var familiarFraud = familiarFraudRiskService.analyse(userId, loanId);
        var takeover = accountTakeoverService.analyse(userId, ipAddress);
        int highestThreat = Math.max(takeover.score(), familiarFraud.score());
        int score = (int) (behaviour.score() * 0.25 + ip.score() * 0.20 + highestThreat * 0.55);
        int enginesTriggered = 0;
        if (behaviour.score() >= 20) enginesTriggered++;
        if (ip.score() >= 50) enginesTriggered++;
        if (familiarFraud.score() >= 30) enginesTriggered++;
        if (takeover.score() >= 30) enginesTriggered++;
        if (enginesTriggered >= 3) score += 20; else if (enginesTriggered >= 2) score += 10;
        score = Math.min(score, 100);
        List<String> reasons = new ArrayList<>();
        reasons.addAll(behaviour.reasons());
        if (ip.malicious()) reasons.add(ip.reason());
        reasons.addAll(familiarFraud.reasons());
        reasons.addAll(takeover.reasons());
        SecuritySeverity severity = severity(score);
        String threatType;
        if (takeover.score() >= familiarFraud.score() && takeover.score() >= 30) threatType = "POSSIBLE_ACCOUNT_TAKEOVER";
        else if (familiarFraud.score() >= 30) threatType = "POSSIBLE_UNAUTHORIZED_LOAN_ACTIVITY";
        else threatType = "GENERAL_SECURITY_ANOMALY";
        return new SecurityRiskAssessment(score, severity, threatType, reasons.stream().distinct().toList());
    }
    private SecuritySeverity severity(int score) {
        if (score >= 81) return SecuritySeverity.CRITICAL;
        if (score >= 61) return SecuritySeverity.HIGH;
        if (score >= 31) return SecuritySeverity.MEDIUM;
        return SecuritySeverity.LOW;
    }
}
