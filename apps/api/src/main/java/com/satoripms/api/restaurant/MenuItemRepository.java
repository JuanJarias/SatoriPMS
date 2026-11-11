package com.satoripms.api.restaurant;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface MenuItemRepository extends JpaRepository<MenuItem, Long> {
    List<MenuItem> findAllByOrderByCategoryAscNameAsc();
    List<MenuItem> findByCategoryAndIsAvailableTrue(String category);
    List<MenuItem> findByIsAvailableTrue();
}
