package com.satoripms.api.review;

import lombok.Data;

@Data
public class ReviewRequestDto {
    private String waId;
    private String comment;
    private Integer rating;
}
